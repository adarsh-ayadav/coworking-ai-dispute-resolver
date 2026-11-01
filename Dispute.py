import os 
import json
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from datetime import datetime
from typing import Literal
from pathlib import Path

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("Groq Api key not found")

client = Groq(api_key = my_api_key)
model = "openai/gpt-oss-120b"

class BookingDetails(BaseModel):
    Customer_Name : str
    Room_Type : Literal["Meeting Room","Private Cabin","Studio","Day Pass"]
    Amount_Paid : float
    Cancellation_time : datetime | None = None
    Issue : str

Bookingschema = BookingDetails.model_json_schema()

class IssueExtraction(BaseModel):
    OnTopic : bool
    IssueResponse : list[Literal["Missing_Aminities","Misleading_Listing", "Access_Failure", "Cancellation", "Property_damge"]]
    details : BookingDetails

IssueSchema = IssueExtraction.model_json_schema()

class EvidanceAnalysis(BaseModel):
    OnTopic : bool
    Customer_Statement : str
    listing_promises: list[str]
    Host_Statement : str | None = None
    PreDefine_Policy : list[str]
    issuedetails : IssueExtraction

EvidenceSchema = EvidanceAnalysis.model_json_schema()

class ResolutonProposal(BaseModel):
    Full_Refund : bool
    Partial_Refund : bool 
    No_Refund : bool 
    Manual_Investigation : bool
    Evidance : EvidanceAnalysis

ResolutionSchema = ResolutonProposal.model_json_schema()

class AdminProposal(BaseModel):
    Approve : bool
    Reject : bool
    Modify : bool
    Resolution : ResolutonProposal

AdminSchema = AdminProposal.model_json_schema()



Sys_prompt =f"""

You are a dispute analyst for a coworking marketplace (meeting rooms, desks, private cabins, studios, day passes). You have fetch details from : {Bookingschema} and You only handle booking disputes.
If the message is not about a booking dispute, set OnTopic to false.
If any details are missing from {Bookingschema} Tell them to fill again the missing details.

Analyze the stages using these schemas:
Issue extraction: {IssueSchema}
Evidence analysis: {EvidenceSchema}
Resolution proposal: {ResolutionSchema}
Admin proposal: {AdminSchema}


POLICY

- CANCELLATION POLICY
- Cancellation more than 24 hours before the booking start time: 100% refund.
- Cancellation between 2 and 24 hours before the booking start time: 50% refund.
- Cancellation less than 2 hours before the booking start time: 0% refund (no refund).

- AMENITY / LISTING MISMATCH POLICY
- If an advertised amenity is verified as not working or missing but the space was otherwise usable: 25% refund.
- If multiple advertised amenities are verified as not working or missing and they materially affected use: 50% refund.
-If the amenity failure is only alleged by the customer and the owner disputes it with no supporting evidence: manual investigation {IssueSchema}.

- ACCESS FAILURE POLICY
- If the customer was verifiably denied access or could not enter the space for the booked slot: 100% refund.
- If access failure is claimed but there is no access log, owner confirmation or other evidence: manual investigation.

- DAMAGE CLAIM POLICY
- Damage claims by the owner require photo or inspection evidence dated before and after the booking {EvidenceSchema}.
- If damage evidence is missing or the customer denies the claim: manual investigation. No automatic deductions are allowed.

- NOISE / ENVIRONMENT POLICY
- Noise complaints are valid only if the listing explicitly promised a quiet environment AND there is supporting evidence (recording, third-party report, staff note).
- If the listing made no quiet promise, no refund. If a quiet promise exists but there is no evidence, manual investigation.

-GENERAL RULES
- AI recommendations are advisory only{ResolutionSchema}.
- A human admin must approve every final decision : {AdminSchema}.
- Refund percentages must be exactly one of the percentages stated in these policies. No other percentages may be used.
- When facts are disputed and critical evidence is unavailable, the outcome must be manual investigation.

Use only the provided policies. Never invent refund percentages or rules.
If facts are disputed or evidence is missing, choose Manual_Investigation.
 
"""

messages = [
    {"role": "system", "content": Sys_prompt},
    {"role": "system", "content": (
                f"Take the details from user {Bookingschema}"
                "Respond only with a valid JSON object with keys: "
                '"OnTopic" (true/false), "Message" (your reply to the customer), '
                '"Missing_Details" (list of missing booking fields). '
                "If the message is off-topic, set OnTopic to false and reply: "
                "'I can only help with disputes about existing bookings. "
                "Please describe the problem with your booking.' Do not mention sales teams or other departments."
)},
]
while True:
    user_prompt = input('Hello Sir Tell me the Booking Details and issue, type "EXIT CHAT"\nTell me about your issue: ').strip()

    if user_prompt in ["EXIT CHAT", "exit chat", "bye", "Bye", "exit", "Exit"]:
        print("Thank you for your time.")
        break

    if not user_prompt:
        continue

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    messages.append({"role": "assistant", "content": raw})

    try:
        print(json.dumps(json.loads(raw), indent=2))
    except json.JSONDecodeError:
        print(raw)
