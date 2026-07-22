import time
import logging

from dataclasses import dataclass
from dataclasses import field

from typing import Optional
from typing import Dict


from rules_engine import scan_text
from llm_classifier import classify


# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(

    level=logging.INFO

)


logger = logging.getLogger(

    "suraksha.session"

)


# ==================================================
# CONFIGURATION
# ==================================================

SCORE_INCREASE_THRESHOLD = 3

HEARTBEAT_SECONDS = 20


# ==================================================
# SESSION
# ==================================================

@dataclass
class CallSession:

    session_id: str

    full_transcript: str = ""

    last_llm_score: int = -1

    last_llm_call_time: float = 0.0

    last_verdict: Optional[dict] = None

    last_error: Optional[str] = None

    created_at: float = field(

        default_factory=time.time

    )


# ==================================================
# SESSION MANAGER
# ==================================================

class SessionManager:


    def __init__(self):


        self._sessions: Dict[

            str,

            CallSession

        ] = {}


    # --------------------------------------------------
    # START SESSION
    # --------------------------------------------------

    def start_session(

        self,

        session_id: str

    ) -> CallSession:


        session = CallSession(

            session_id=
                session_id

        )


        self._sessions[

            session_id

        ] = session


        return session


    # --------------------------------------------------
    # GET SESSION
    # --------------------------------------------------

    def get_session(

        self,

        session_id: str

    ) -> Optional[CallSession]:


        return self._sessions.get(

            session_id

        )


    # --------------------------------------------------
    # ADD TRANSCRIPT
    # --------------------------------------------------

    def add_transcript_chunk(

        self,

        session_id: str,

        chunk_text: str

    ) -> dict:


        session = self.get_session(

            session_id

        )


        if session is None:


            session = self.start_session(

                session_id

            )


        # Add transcript chunk

        session.full_transcript = (

            session.full_transcript

            + " "

            + chunk_text

        ).strip()



        # Run free rules engine

        rules_result = scan_text(

            session.full_transcript

        )


        rules_dict = (

            rules_result.to_dict()

        )



        # Decide whether Claude should run

        should_call_llm = (

            self._should_call_llm(

                session,

                rules_result.total_score

            )

        )



        llm_called_this_turn = False

        llm_error = None



        # --------------------------------------------------
        # AI ANALYSIS
        # --------------------------------------------------

        if should_call_llm:


            try:


                verdict = classify(

                    session.full_transcript,

                    rules_dict

                )


                session.last_verdict = (

                    verdict

                )


                session.last_llm_score = (

                    rules_result.total_score

                )


                session.last_llm_call_time = (

                    time.time()

                )


                session.last_error = None


                llm_called_this_turn = True



            except Exception as error:


                llm_error = str(

                    error

                )


                session.last_error = (

                    llm_error

                )


                logger.error(

                    "Claude classification failed "
                    "for session %s: %s",

                    session_id,

                    error

                )



        # --------------------------------------------------
        # RETURN CURRENT STATE
        # --------------------------------------------------

        return {


            "rules_result":

                rules_dict,


            "verdict":

                session.last_verdict,


            "llm_called_this_turn":

                llm_called_this_turn,


            "llm_error":

                llm_error,


            "full_transcript":

                session.full_transcript

        }


    # --------------------------------------------------
    # SHOULD CALL AI?
    # --------------------------------------------------

    def _should_call_llm(

        self,

        session: CallSession,

        current_score: int

    ) -> bool:


        # No suspicious signal means there is
        # no reason to spend an API request.

        if current_score <= 0:

            return False



        # First suspicious signal

        if session.last_llm_score == -1:

            return True



        # Risk increased significantly

        if (

            current_score

            - session.last_llm_score

            >= SCORE_INCREASE_THRESHOLD

        ):

            return True



        # Periodic heartbeat

        if (

            session.last_verdict

            is not None

        ):


            elapsed = (

                time.time()

                - session.last_llm_call_time

            )


            if (

                elapsed

                >= HEARTBEAT_SECONDS

            ):

                return True



        # If the previous Claude request failed,
        # retry when another transcript chunk arrives.

        if (

            session.last_error

            is not None

        ):

            return True



        return False