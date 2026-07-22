import os
import json

from anthropic import Anthropic


# ==================================================
# CONFIGURATION
# ==================================================

API_KEY = os.getenv(
    "ANTHROPIC_API_KEY"
)


MODEL = os.getenv(
    "ANTHROPIC_MODEL",
    "claude-sonnet-5"
)


# ==================================================
# SYSTEM PROMPT
# ==================================================

SYSTEM_PROMPT = """
You are the AI reasoning layer of Suraksha Shield, a real-time
digital scam detection system.

Your task is to analyze an ongoing phone-call transcript and determine
whether the conversation shows signs of fraud or a digital arrest scam.

IMPORTANT SAFETY CONTEXT:

Indian law-enforcement agencies do not place citizens under
"digital arrest" over phone calls or video calls.

Legitimate police, CBI, customs, RBI, courts, banks, and government
agencies do not require a person to transfer money to a so-called
"safe account", "verification account", or "RBI monitoring account"
to prove innocence.

Requests for OTPs, UPI PINs, banking passwords, remote screen access,
or urgent money transfers are major warning signs.

Scammers may impersonate:

- Police
- CBI
- Customs
- Cyber Crime officers
- RBI
- Courts
- Courier companies
- Banks

Common manipulation techniques include:

- Threatening arrest
- Claiming illegal parcels or drugs were found
- Ordering the victim to stay on the call
- Preventing the victim from speaking to family
- Creating extreme urgency
- Requesting money transfers
- Asking for OTPs or banking credentials

The rules engine findings provided to you are evidence, not an
automatic verdict.

Consider the complete conversation context.

A legitimate conversation may contain words such as "bank",
"courier", or "police" without being fraudulent.

Return ONLY valid JSON.

Use exactly this structure:

{
    "verdict": "safe | suspicious | likely_scam | scam",
    "confidence": 0,
    "red_flags": [],
    "explanation": "",
    "action_steps": []
}

The confidence value must be an integer between 0 and 100.

Keep the explanation concise.

If there is a significant scam risk, action_steps should prioritize:

1. Do not transfer money.
2. Do not share OTP, PIN, passwords, or banking credentials.
3. Disconnect and independently verify the caller.
4. Contact appropriate official channels if money was transferred.
"""


# ==================================================
# CLASSIFIER
# ==================================================

def classify(
    transcript: str,
    rules_result: dict
) -> dict:


    if not API_KEY:

        raise RuntimeError(

            "ANTHROPIC_API_KEY is not set."

        )


    client = Anthropic(

        api_key=API_KEY

    )


    user_message = f"""
Analyze this ongoing call.

TRANSCRIPT:

{transcript}


RULES ENGINE FINDINGS:

{json.dumps(
    rules_result,
    indent=2
)}


Return only the required JSON object.
"""


    response = client.messages.create(

        model=MODEL,

        max_tokens=1000,

        temperature=0,

        system=SYSTEM_PROMPT,

        messages=[

            {

                "role":
                    "user",

                "content":
                    user_message

            }

        ]

    )


    if not response.content:

        raise RuntimeError(

            "Claude returned an empty response."

        )


    raw_text = (

        response

        .content[0]

        .text

        .strip()

    )


    # Remove markdown fences if the model
    # unexpectedly returns them.

    if raw_text.startswith("```"):


        raw_text = raw_text.replace(

            "```json",

            "",

            1

        )


        raw_text = raw_text.replace(

            "```",

            ""

        )


        raw_text = raw_text.strip()


    try:


        verdict = json.loads(

            raw_text

        )


    except json.JSONDecodeError as error:


        raise RuntimeError(

            f"Claude returned invalid JSON: {raw_text}"

        ) from error


    required_fields = [

        "verdict",

        "confidence",

        "red_flags",

        "explanation",

        "action_steps"

    ]


    for field in required_fields:


        if field not in verdict:


            raise RuntimeError(

                f"Claude response missing field: {field}"

            )


    allowed_verdicts = {

        "safe",

        "suspicious",

        "likely_scam",

        "scam"

    }


    if (

        verdict["verdict"]

        not in allowed_verdicts

    ):


        raise RuntimeError(

            "Claude returned an invalid verdict."

        )


    try:

        verdict["confidence"] = int(

            verdict["confidence"]

        )


    except (TypeError, ValueError):

        verdict["confidence"] = 0


    verdict["confidence"] = max(

        0,

        min(

            100,

            verdict["confidence"]

        )

    )


    if not isinstance(

        verdict["red_flags"],

        list

    ):

        verdict["red_flags"] = []


    if not isinstance(

        verdict["action_steps"],

        list

    ):

        verdict["action_steps"] = []


    return verdict