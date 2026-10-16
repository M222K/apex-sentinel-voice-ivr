import asyncio
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Apex Sentinel Voice Webhook Engine", version="1.0.0")

# --- Concept: Session Parameter Parser ---

class ProtobufPayloadParser:
    """Safely extracts session parameters passed by Dialogflow CX."""
    @staticmethod
    def extract_session_parameters(webhook_request: Dict[str, Any]) -> Dict[str, Any]:
        return webhook_request.get("sessionInfo", {}).get("parameters", {})

# --- Concept: OOP Service Layer ---
class BankingService:
    def __init__(self):
        self._lock_card = None
        self._get_account_summary = None

    async def lock_card(self, caller_id: str, card_last_four: str) -> bool:
        # Simulate an async database execution delay (80 milliseconds)
        await asyncio.sleep(0.08)
        return True

    async def get_account_summary(self, account_id: str) -> Dict[str, Any]:
        # Simulate an async database fetch delay (100 milliseconds)
        await asyncio.sleep(0.10)
        return {
            "account_id": account_id,
            "balance": 12450.80,
            "status": "ACTIVE"
        }

# Instantiate the service once for the application lifecycle
banking_service = BankingService()

# --- Concept: Tool Webhook Endpoint ---


@app.post("/api/v1/tools/lock-card")
async def handle_card_lock(request: Request) -> Dict[str, Any]:
    raw_payload = await request.json()
    params = ProtobufPayloadParser.extract_session_parameters(raw_payload)

    caller_id = params.get("caller_id", "UNKNOWN")
    card_last_four = params.get("card_last_four", "0000")

    success = await banking_service.lock_card(caller_id, card_last_four)

    if success:
        # Return Dialogflow CX-compliant sessionInfo updates and conversational messages
        return {
            "sessionInfo": {
                "parameters": {
                    "card_status": "LOCKED"
                }
            },
            "fulfillment_response": {
                "messages": [{
                    "text": {
                        "text": [f"Your card ending in {card_last_four} has been successfully locked."]
                    }
                }]
            }
        }
    raise HTTPException(status_code=500, detail="Failed to lock card")


@app.post("/api/v1/tools/get-balance")
async def handle_get_balance(request: Request) -> Dict[str, Any]:
    raw_payload = await request.json()
    params = ProtobufPayloadParser.extract_session_parameters(raw_payload)
    account_id = params.get("account_id", "ACC-1001")

    account = await banking_service.get_account_summary(account_id)
    return {
        "sessionInfo": {
            "parameters": {
                "account_balance": account["balance"]
            }
        },
        "fulfillment_response": {
            "messages": [{
                "text": {
                    "text": [f"Your available balance is {account['balance']:.2f} dollars."]
                }
            }]
        }
    }
