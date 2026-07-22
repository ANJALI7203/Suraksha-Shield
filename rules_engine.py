from dataclasses import dataclass
from typing import List, Dict


# ==================================================
# SIGNAL DEFINITIONS
# ==================================================

SIGNALS = [

    # --------------------------------------------------
    # AUTHORITY IMPERSONATION
    # --------------------------------------------------

    (
        "authority_impersonation",
        2,
        [
            "cbi",
            "crime branch",
            "cyber crime",
            "cyber police",
            "police officer",
            "customs officer",
            "narcotics department",
            "narcotics bureau",
            "enforcement directorate",
            "supreme court",
            "court officer",
            "mumbai police",
            "delhi police",

            # Hinglish
            "main cbi se bol raha",
            "main police se bol raha",
            "police se baat kar raha",
            "cyber crime department se",
            "custom officer",
        ]
    ),


    # --------------------------------------------------
    # DIGITAL ARREST
    # --------------------------------------------------

    (
        "digital_arrest",
        5,
        [
            "digital arrest",
            "digitally arrested",
            "under digital arrest",
            "virtual arrest",

            # Hindi / Hinglish
            "digital arrest mein",
            "aap digital arrest mein hain",
            "aapko digital arrest",
        ]
    ),


    # --------------------------------------------------
    # ARREST / LEGAL THREATS
    # --------------------------------------------------

    (
        "arrest_threat",
        4,
        [
            "arrest warrant",
            "warrant against you",
            "you will be arrested",
            "we will arrest you",
            "police will arrest you",
            "legal action against you",
            "criminal case against you",
            "case has been registered",
            "fir registered",
            "fir against you",

            # Hinglish
            "aapko arrest",
            "aap arrest ho jayenge",
            "arrest warrant hai",
            "aapke naam warrant",
            "aapke khilaf case",
            "case register hua hai",
        ]
    ),


    # --------------------------------------------------
    # PARCEL / COURIER SCAMS
    # --------------------------------------------------

    (
        "parcel_scam",
        2,
        [
            "courier company",
            "illegal parcel",
            "suspicious parcel",
            "parcel contains drugs",
            "parcel containing drugs",
            "banned substance",
            "illegal substance",
            "customs has seized",
            "customs seized",
            "parcel has been seized",
            "package has been seized",
            "fedex parcel",

            # Hinglish
            "aapka parcel",
            "parcel mein drugs",
            "parcel mein illegal",
            "parcel seize",
            "courier se bol raha",
        ]
    ),


    # --------------------------------------------------
    # SECRECY / ISOLATION
    # --------------------------------------------------

    (
        "isolation",
        3,
        [
            "don't tell anyone",
            "do not tell anyone",
            "don't inform anyone",
            "do not inform anyone",
            "don't tell your family",
            "do not tell your family",
            "keep this confidential",
            "keep this secret",
            "stay on the call",
            "do not disconnect",
            "don't disconnect",
            "remain on video call",

            # Hinglish
            "kisi ko mat batana",
            "ghar walon ko mat batana",
            "family ko mat batana",
            "call mat kaatna",
            "phone mat kaatna",
            "call disconnect mat karna",
            "line par rahiye",
            "call par rahiye",
        ]
    ),


    # --------------------------------------------------
    # MONEY TRANSFER
    # --------------------------------------------------

    (
        "money_transfer",
        4,
        [
            "transfer money",
            "transfer the money",
            "send money",
            "make payment",
            "security deposit",
            "verification amount",
            "verification payment",
            "safe account",
            "safe custody account",
            "monitoring account",
            "rbi monitoring account",
            "government account",
            "temporary account",
            "fund verification",

            # Hinglish
            "paise transfer",
            "paisa transfer",
            "payment karo",
            "payment kijiye",
            "paise bhejo",
            "paisa bhejo",
            "account mein transfer",
        ]
    ),


    # --------------------------------------------------
    # OTP / CREDENTIAL REQUEST
    # --------------------------------------------------

    (
        "credential_request",
        5,
        [
            "share your otp",
            "tell me the otp",
            "send the otp",
            "give me the otp",
            "share otp",
            "upi pin",
            "share your pin",
            "bank password",
            "internet banking password",
            "card number",
            "cvv",
            "screen sharing",
            "share your screen",

            # Hinglish
            "otp batao",
            "otp bataiye",
            "otp share karo",
            "otp bhejo",
            "pin batao",
            "upi pin batao",
            "screen share karo",
        ]
    ),


    # --------------------------------------------------
    # URGENCY / PRESSURE
    # --------------------------------------------------

    (
        "urgency",
        2,
        [
            "immediately",
            "right now",
            "within 10 minutes",
            "within ten minutes",
            "last chance",
            "urgent action",
            "act immediately",
            "before it is too late",

            # Hinglish
            "abhi karo",
            "turant karo",
            "jaldi karo",
            "abhi transfer",
            "turant transfer",
        ]
    ),


    # --------------------------------------------------
    # REMOTE ACCESS
    # --------------------------------------------------

    (
        "remote_access",
        5,
        [
            "download anydesk",
            "install anydesk",
            "download teamviewer",
            "install teamviewer",
            "remote access",
            "screen sharing app",
            "install this app",
            "download this app",
        ]
    ),
]


# ==================================================
# MATCH RESULT
# ==================================================

@dataclass
class MatchedSignal:

    category: str

    severity: int

    matched_text: str


    def to_dict(self):

        return {

            "category":
                self.category,

            "severity":
                self.severity,

            "matched_text":
                self.matched_text

        }


# ==================================================
# RULE RESULT
# ==================================================

@dataclass
class RulesResult:

    matched_signals: List[MatchedSignal]

    total_score: int

    category_breakdown: Dict[str, int]

    categories_hit: int


    def to_dict(self):

        return {

            "matched_signals": [

                signal.to_dict()

                for signal

                in self.matched_signals

            ],

            "total_score":
                self.total_score,

            "category_breakdown":
                self.category_breakdown,

            "categories_hit":
                self.categories_hit

        }


# ==================================================
# SCAN TEXT
# ==================================================

def scan_text(text: str) -> RulesResult:

    normalized_text = (

        text

        .lower()

        .strip()

    )


    matched_signals = []

    category_breakdown = {}


    for (

        category,

        severity,

        phrases

    ) in SIGNALS:


        category_matches = []


        for phrase in phrases:


            if phrase in normalized_text:


                category_matches.append(

                    phrase

                )


        if category_matches:


            # Count each category once toward the score.
            # This prevents repeated related phrases from
            # inflating the risk score excessively.

            category_breakdown[category] = (

                severity

            )


            for phrase in category_matches:


                matched_signals.append(

                    MatchedSignal(

                        category=
                            category,

                        severity=
                            severity,

                        matched_text=
                            phrase

                    )

                )


    total_score = sum(

        category_breakdown.values()

    )


    return RulesResult(

        matched_signals=
            matched_signals,

        total_score=
            total_score,

        category_breakdown=
            category_breakdown,

        categories_hit=
            len(category_breakdown)

    )