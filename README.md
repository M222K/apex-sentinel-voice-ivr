# 🛡️ Apex Sentinel — Enterprise Voice IVR & Agentic Banking Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Dialogflow CX](https://img.shields.io/badge/Dialogflow_CX-Playbooks_Generative-4285F4?style=flat&logo=googlecloud)](https://cloud.google.com/dialogflow/cx/docs)
[![Twilio](https://img.shields.io/badge/Twilio-Studio_Flow_Voice-F22F46?style=flat&logo=twilio)](https://www.twilio.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://www.python.org/)

**Apex Sentinel** is an enterprise-grade, voice-first Interactive Voice Response (IVR) banking assistant powered by **Dialogflow CX Playbooks** (Generative AI) and a **modular FastAPI backend**. Connected directly to live telephony via **Twilio Studio Flow**, it delivers deterministic execution, strict speech validation, real-time OTP authentication, balance inquiries, and automated fraud security card locking.

---

## 🏛️ System Architecture

```
                               ┌─────────────────────────────────────────┐
                               │           Caller (Cellular/PSTN)        │
                               └────────────────────┬────────────────────┘
                                                    │ Voice Call
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │       Twilio Telephony & Studio Flow    │
                               │     (Connect Virtual Agent Stream)      │
                               └────────────────────┬────────────────────┘
                                                    │ Stream Connector / Webhook
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │       Dialogflow CX Agent Studio        │
                               │          (Draft Environment)            │
                               └────────────────────┬────────────────────┘
                                                    │
                 ┌──────────────────────────────────┼──────────────────────────────────┐
                 │                                  │                                  │
                 ▼                                  ▼                                  ▼
   ┌──────────────────────────┐       ┌──────────────────────────┐       ┌──────────────────────────┐
   │    Auth Verification     │       │     Account Services     │       │      Fraud Security      │
   │        Sub-Agent         │       │        Sub-Agent         │       │        Sub-Agent         │
   └─────────────┬────────────┘       └─────────────┬────────────┘       └─────────────┬────────────┘
                 │                                  │                                  │
                 └──────────────────────────────────┼──────────────────────────────────┘
                                                    │ OpenAPI 3.0 Tool Execution
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │        FastAPI Async Webhook API        │
                               │         (Uvicorn + APIRouters)          │
                               └────────────────────┬────────────────────┘
                                                    │
                 ┌──────────────────────────────────┼──────────────────────────────────┐
                 │                                  │                                  │
                 ▼                                  ▼                                  ▼
    GET/POST /api/v1/auth/*            GET/POST /api/v1/account/*         GET/POST /api/v1/fraud/*
    • send-otp                         • balance                          • lock-card
    • verify-otp                       • transactions
```

---

## ✨ Key Technical Highlights

### 1. Deterministic Playbook Execution with Conditional Actions
* **Regex Input Enforcement:** Strict input validation blocks invalid prompts before triggering backend webhooks (e.g., `^\d{6}$` for Account IDs, `^\d{4}$` for OTPs).
* **Progressive Telephony Fallbacks:** 3-tier progressive retry counters for `No-Input` (silence) and `No-Match` (unrecognized speech) events, escalating to human operators cleanly without getting stuck in infinite loops.

### 2. Universal Session Parameter Contract
* **Loop Prevention:** Standardized global session parameters across all playbooks:
  * `$session.params.is_authenticated` (`Boolean`): Retains identity state across sub-agents.
  * `$session.params.account_id` (`String`): Stores the verified 6-digit user identifier.
  * `$session.params.user_satisfied` (`Boolean`): Clean completion flag set by child playbooks on completion, allowing the Root Playbook to execute a warm farewell and trigger `END_CALL`.


---

## 📁 Repository Structure

```text
apex-sentinel-ivr/
├── app/
│   ├── main.py                     # App entry point, OpenAPI metadata & router mounts
│   ├
│   └── schemas/
│       └── openapi_schema.json            # OpenAPI 3.0 schema importable directly into Dialogflow Tools
├── dialogflow/
│
├── telephony/
│   ├── twilio_studio_flow.json     # Exported Twilio Studio Flow connector definition
│
├── requirements.txt                # Python package dependencies
└── README.md                       # Master system documentation
```

## 🚀 Local Setup & Installation

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/your-username/apex-sentinel-ivr.git
cd apex-sentinel-ivr

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

```env
PORT=8000
ENVIRONMENT=development
GCP_PROJECT_ID=your-gcp-project-id
DIALOGFLOW_LOCATION=global
DIALOGFLOW_AGENT_ID=your-agent-id
```

### 3. Launch the FastAPI Webhook Server

From the project root directory, run Uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify your server is live by opening `http://127.0.0.1:8000/docs` to test interactive OpenAPI endpoints.

---

## 📞 Twilio Telephony & Live Deployment

### 1. Start Local Tunneling via ngrok

Expose your local FastAPI server to Google Cloud and Twilio:

```bash
ngrok http 8000
```

Copy the generated HTTPS URL (e.g., `https://a1b2c3.ngrok-free.app`).

### 2. Bind OpenAPI Schema in Dialogflow CX

1. Go to **Dialogflow CX Console** > **Manage** > **Tools** > `Apex_Banking_Tool`.
2. Update the `servers.url` field in your tool's OpenAPI schema:
   ```yaml
   servers:
     - url: https://a1b2c3.ngrok-free.app
   ```
3. Save the tool changes.

### 3. Connect Twilio Studio Flow

1. In **Twilio Console**, go to **Studio** > **Flows** and import `telephony/twilio_studio_flow.json`.
2. Connect your active US/Local Twilio Phone Number to the Studio Flow under **Voice Configuration**.
3. Dial the number from any phone to test end-to-end voice interactions!

---

## 🧪 Validated Telephony Call Trace

```text
[TELEPHONY TRACE LOG — REAL TEST RUN]
- Call SID: CA48f93a20e821049c81a293b019a
- Dialed Number: +1 (202) 555-0199

[00:01] AGENT: "Welcome to Apex Sentinel Voice Banking. Please state your 6-digit Account ID."
[00:05] CALLER: "1 2 3 4 5 6" 
        └─► Matched regex ^\d{6}$ 
        └─► Webhook POST /api/v1/auth/send-otp ──► 200 OK (190ms)
[00:08] AGENT: "I sent a 4-digit security code to your mobile. Please enter or speak the 4 digits."
[00:12] CALLER: "1 2 3 4"
        └─► Matched regex ^\d{4}$
        └─► Webhook POST /api/v1/auth/verify-otp ──► 200 OK (175ms)
[00:15] AGENT: "Authentication successful. How can I assist you today?"
[00:17] CALLER: "Lock my card immediately."
        └─► Route: Fraud Security Sub-Agent
        └─► Webhook POST /api/v1/fraud/lock-card ──► 200 OK (210ms)
[00:20] AGENT: "Your card ending in 1234 has been successfully locked. Do you need any other help today?"
[00:23] CALLER: "No thanks, that is all."
        └─► Set $session.params.user_satisfied = true
        └─► Return to Default Root Playbook
[00:25] AGENT: "Thank you for calling Apex Sentinel. Have a great day! Goodbye."
        └─► Action: END_CALL [Session Terminated Cleanly]
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more details.