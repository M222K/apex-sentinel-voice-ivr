# 🛡️ Apex Sentinel — Enterprise Voice IVR & Security Engine

**Apex Sentinel** is a production-grade, voice-first Interactive Voice Response (IVR) and conversational AI system built for enterprise banking operations. It bridges low-latency voice AI orchestration with secure backend banking tools—featuring root-level OTP multi-factor authentication, explicit voice re-clarification loops, card security management, and real-time account telemetry.

---

## 🏛️ System Architecture

```
                                  [ Incoming Voice Call ]
                                             │
                                             ▼
                          [ Dialogflow CX Root Playbook Gatekeeper ]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │  Is Session Authenticated? (is_auth=true) │
                       └─────────────────────┬─────────────────────┘
                                             │
                           NO ───────────────┴─────────────── YES
                           │                                   │
                           ▼                                   ▼
              [ Auth Sub-Agent ]                     [ Service Sub-Playbooks ]
             ┌──────────────────┐               ┌─────────────────────────────────┐
             │ 1. Request ID    │               │                                 │
             │ 2. Trigger OTP   │               ├─► [ Account Services Sub-Agent ]│
             │ 3. Confirm Input │               │    └─► Fetch Balance            │
             │ 4. Verify Code   │               │                                 │
             └─────────┬────────┘               ├─► [ Fraud Security Sub-Agent ]  │
                       │                        │    └─► Lock/Block Card          │
                       ▼                        └─────────────────────────────────┘
             (Passes is_auth=true)                              │
                       │                                        │
                       └────────────────────┬───────────────────┘
                                            │
                                            ▼ (HTTPS POST over Tunnel)
                             [ FastAPI Webhook Engine ]
                                            │
                       ┌────────────────────┼────────────────────┐
                       ▼                    ▼                    ▼
                `/send-otp`           `/verify-otp`        `/lock-card`
                `/get-balance`
```

---

## ✨ Key Features & Enterprise Engineering Highlights

- **🔐 Root Security Gatekeeper:** Enforces multi-factor authentication (OTP) at the conversation root *before* delegating control to domain-specific playbooks.
- **🎙️ Voice-Optimized Parameter Confirmation:** Built-in explicit voice read-back loops ("*I heard the digits as 2 3 4 5, is that correct?*") designed specifically to mitigate Speech-to-Text (STT) noise in voice environments.
- **🧩 Modular Playbook Topology:** Multi-agent design separating **Identity Verification**, **Account Services**, and **Fraud Management** into decoupled, reusable sub-playbooks.
- **⚡ Async FastAPI Webhook Backend:** High-performance RESTful API using Python 3.10+, FastAPI, and Pydantic for sub-second tool execution and data validation.
- **📄 Formal API Contracts:** Full OpenAPI 3.0 specification (`openapi_schema.json`) defining strict request/response models for Dialogflow CX integration.
- **📞 Enterprise Telephony Ready:** Designed for seamless integration with enterprise telephony stacks including **Genesys Cloud CX** (Architect), **Twilio Media Streams**, and **Dialogflow CX Phone Gateway**.

---

## 📁 Repository Structure

```text
apex-sentinel-voice-ivr/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI webhook endpoints & tool handlers
├── agent/
│   └── agent_export.json    # Complete Dialogflow CX Agent Playbook export
├── openapi_schema.json      # OpenAPI 3.0 specification for Dialogflow Tools
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- [ngrok](https://ngrok.com/) (for tunneling local webhook to Google Cloud)
- Google Cloud / Dialogflow CX Agent Studio account

### 1. Clone & Setup Environment
```bash
git clone https://github.com/YOUR_USERNAME/apex-sentinel-voice-ivr.git
cd apex-sentinel-voice-ivr

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
*The server will start at `http://127.0.0.1:8000` with interactive API docs at `http://127.0.0.1:8000/docs`.*

### 3. Expose Local Server via ngrok
In a separate terminal window, expose port 8000:
```bash
ngrok http 8000
```
Copy the generated HTTPS URL (e.g., `https://xxxx-xx-xx.ngrok-free.app`).

---

## 🤖 Dialogflow CX Setup

1. Open **Dialogflow CX Console**.
2. Create a new agent or select an existing one.
3. Go to **Agent Settings ⚙️** > **Export/Import** > **Import** and upload `agent/agent_export.json`.
4. Navigate to **Tools** > **Apex Banking Tools**.
5. Update the OpenAPI schema base URL with your active ngrok URL:
   ```json
   "servers": [
     {
       "url": "https://YOUR_NGROK_URL.ngrok-free.app"
     }
   ]
   ```
6. Test interactions directly in the **Dialogflow Simulator** or assign a phone number via **Manage > Integrations > Dialogflow Phone Gateway**.

---

## 📡 Webhook API Contract

| Endpoint | Method | Description | Primary Parameters |
| :--- | :---: | :--- | :--- |
| `/api/v1/tools/send-otp` | `POST` | Dispatches 4-digit OTP to user mobile | `account_id` |
| `/api/v1/tools/verify-otp` | `POST` | Verifies spoken/keyed 4-digit OTP | `account_id`, `user_otp` |
| `/api/v1/tools/lock-card` | `POST` | Locks a compromised credit/debit card | `caller_id`, `card_last_four` |
| `/api/v1/tools/get-balance` | `POST` | Queries available balance details | `account_id` |

---

## 🧪 Conversation Test Script

```text
Caller: "Hi, I need to check my balance."
Agent: "I can help with that. First, to secure your account, please provide your account ID."
Caller: "ACC-1001"
Agent: "I have sent a four-digit OTP to your registered phone number. What is the code?"
Caller: "1234"
Agent: "I heard 1 2 3 4, is that correct?"
Caller: "Yes"
Agent: "Authentication successful. Your available balance for account ACC-1001 is 12,450 dollars."
```

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more details.