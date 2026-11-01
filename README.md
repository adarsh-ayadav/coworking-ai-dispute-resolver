# Coworking AI Dispute Resolver

An AI-powered command-line assistant that handles **booking disputes for a coworking marketplace** (meeting rooms, private cabins, studios, and day passes). It collects booking details from the customer, checks for missing information, and applies a fixed refund policy to produce a structured, advisory recommendation. A human admin always makes the final decision.

Built with Python, the [Groq API](https://console.groq.com/), and Pydantic.

---

## Features

- **Conversational intake** – a terminal chat that asks the customer to describe their booking and issue.
- **Missing-detail detection** – flags any required booking fields the customer hasn't provided and asks them to fill them in.
- **Off-topic guard** – only handles booking disputes; anything else gets `OnTopic: false` and a polite redirect.
- **Policy-grounded decisions** – the model is restricted to the predefined policies below and may never invent refund percentages.
- **Structured JSON output** – responses are returned as valid JSON (`response_format = json_object`).
- **Human-in-the-loop** – AI recommendations are advisory only; every final decision requires admin approval.

---

## How It Works

The dispute pipeline is modelled with Pydantic schemas, which are injected into the system prompt:

| Stage | Schema | Purpose |
|---|---|---|
| 1. Booking | `BookingDetails` | Customer name, room type, amount paid, cancellation time, issue |
| 2. Issue extraction | `IssueExtraction` | On-topic check and issue category |
| 3. Evidence analysis | `EvidanceAnalysis` | Customer/host statements, listing promises, applicable policies |
| 4. Resolution proposal | `ResolutonProposal` | Full refund / partial refund / no refund / manual investigation |
| 5. Admin decision | `AdminProposal` | Approve / reject / modify |

**Supported room types:** `Meeting Room`, `Private Cabin`, `Studio`, `Day Pass`

**Issue categories:** `Missing_Aminities`, `Misleading_Listing`, `Access_Failure`, `Cancellation`, `Property_damge`

---

## Policies Enforced

**Cancellation**
- More than 24 hours before start: 100% refund
- Between 2 and 24 hours before start: 50% refund
- Less than 2 hours before start: no refund

**Amenity / listing mismatch**
- One verified missing or broken amenity, space otherwise usable: 25% refund
- Multiple verified failures that materially affected use: 50% refund
- Alleged by customer only and disputed by owner with no evidence: manual investigation

**Access failure**
- Verifiably denied access: 100% refund
- Claimed without logs or evidence: manual investigation

**Damage claims**
- Owner must supply dated before/after photos or inspection evidence
- Missing evidence or customer denies: manual investigation (no automatic deductions)

**Noise / environment**
- Valid only if the listing promised quiet **and** evidence exists
- No quiet promise: no refund; promise but no evidence: manual investigation

**General rules**
- Refund percentages must be exactly one of those listed above.
- When facts are disputed and critical evidence is missing, the outcome is manual investigation.

---

## Tech Stack

- Python 3.14+
- [Groq SDK](https://pypi.org/project/groq/) (model: `openai/gpt-oss-120b`)
- [Pydantic](https://docs.pydantic.dev/) v2
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [uv](https://docs.astral.sh/uv/) for dependency management

---

## Getting Started

### Prerequisites

- Python 3.14 or newer
- A free [Groq API key](https://console.groq.com/keys)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip

### Installation

```bash
git clone https://github.com/<your-username>/coworking-ai-dispute-resolver.git
cd coworking-ai-dispute-resolver
```

Install dependencies with uv:

```bash
uv sync
```

Or with pip:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install groq pydantic python-dotenv
```

### Configuration

Copy the example environment file and add your key:

```bash
cp .env.example .env
```

```env
GROQ_API_KEY=your_groq_api_key_here
```

> **Never commit your `.env` file.** It is listed in `.gitignore`.

### Run

```bash
uv run Dispute.py
# or
python Dispute.py
```

Type `exit`, `EXIT CHAT`, or `bye` to quit.

---

## Example Session

```text
Hello Sir Tell me the Booking Details and issue, type "EXIT CHAT"
Tell me about your issue: I booked a private cabin, paid 1500, but the Wi-Fi was not working.
```

Example response shape:

```json
{
  "OnTopic": true,
  "Message": "Thanks for reporting this. Please also share your name and ...",
  "Missing_Details": ["Customer_Name"]
}
```

---

## Project Structure

```text
coworking-ai-dispute-resolver/
├── Dispute.py                       # Main chat application
├── src/cowworking_ai_dispute/       # Package scaffold (entry point placeholder)
├── pyproject.toml                   # Project metadata and dependencies
├── uv.lock                          # Locked dependency versions
├── .python-version                  # Python version pin
├── .env.example                     # Template for environment variables
├── .gitignore
└── README.md
```

---

## Limitations and Roadmap

- [ ] Validate model output against the Pydantic models (schemas are currently used in the prompt only)
- [ ] Return the full resolution proposal (refund decision + evidence) in the JSON output
- [ ] Add an admin review step (approve / reject / modify) in the CLI
- [ ] Move `Dispute.py` into the `src/` package and wire up the `main()` entry point
- [ ] Add unit tests for policy scenarios
- [ ] Persist dispute history to a database or file
- [ ] Build a web interface

---

## Disclaimer

This tool provides **advisory recommendations only**. All refund decisions must be reviewed and approved by a human administrator.

---

## Author

**Adarsh** – [adarshyadav7252@gmail.com](mailto:adarshyadav7252@gmail.com)

