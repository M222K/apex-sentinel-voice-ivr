import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import random



# Initialize FastAPI app
app = FastAPI(
    title="Apex Sentinel Voice Webhook Engine",
    description="Core backend webhook service for Dialogflow CX / CX Agent Studio voice tools.",
    version="1.0.0",
)

# Enable CORS for cross-origin tool execution
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware to bypass the ngrok browser warning page automatically
@app.middleware("http")
async def add_ngrok_skip_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# Temporary in-memory OTP storage: { "phone_or_account": "1234" }
otp_store: Dict[str, str] = {}


class SendOTPRequest(BaseModel):
    account_id: str = Field(...,description="Target account or user phone identifier")


class VerifyOTPRequest(BaseModel):
    account_id: str = Field(...,description="Target account or user phone identifier")
    user_otp: str = Field(...,description="The 4-digit OTP provided by the caller")



# --- Pydantic Request Models ---
class LockCardRequest(BaseModel):
    caller_id: Optional[str] = Field(
        default=None, description="Unique caller or customer ID"
    )
    card_last_four: str = Field(
        ..., description="The last 4 digits of the card to lock", example="4562"
    )


class GetBalanceRequest(BaseModel):
    account_id: Optional[str] = Field(
        default="ACC-1001", description="Target bank account ID"
    )


# --- Root Endpoint ---
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Apex Sentinel Webhook Engine",
        "docs_url": "/docs",
    }


# --- Tool 1: Lock Card Endpoint ---
@app.post("/api/v1/tools/lock-card")
async def lock_card(payload: LockCardRequest) -> Dict[str, Any]:
    """
    Locks a credit or debit card immediately upon request.
    """
    # Simulate database lock operation
    await asyncio.sleep(0.1)

    return {
        "status": "success",
        "card_last_four": payload.card_last_four,
        "message": f"Your card ending in {payload.card_last_four} has been successfully locked.",
        "action_taken": "CARD_LOCKED",
    }


# --- Tool 2: Get Balance Endpoint ---
@app.post("/api/v1/tools/get-balance")
async def get_balance(payload: GetBalanceRequest) -> Dict[str, Any]:
    """
    Retrieves real-time account balance details.
    """
    # Simulate account database lookup
    await asyncio.sleep(0.1)

    return {
        "status": "success",
        "account_id": payload.account_id or "ACC-1001",
        "available_balance": 12450.80,
        "currency": "USD",
        "message": "Your available account balance is 12,450 dollars and 80 cents.",
    }


@app.post("/api/v1/tools/send-otp")
async def send_otp(payload: SendOTPRequest) -> Dict[str, Any]:
    # Generate a random 4-digit code (for testing, fix to "1234" or generate dynamically)
    generated_otp = str(random.randint(1000, 9999))
    otp_store[payload.account_id] = generated_otp

    # In production: invoke SMS service (Twilio/AWS SNS) here
    print(
        f"[SMS SERVICE MOCK] Sent OTP {generated_otp} to user {payload.account_id}")

    return {
        "status": "success",
        "account_id": payload.account_id,
        "message": f"An OTP has been dispatched to the mobile number registered with account {payload.account_id}."
    }


@app.post("/api/v1/tools/verify-otp")
async def verify_otp(payload: VerifyOTPRequest) -> Dict[str, Any]:
    # Default to 1234 for sandbox testing
    stored_otp = otp_store.get(payload.account_id, "1234")

    if payload.user_otp == stored_otp:
        return {
            "authenticated": True,
            "status": "success",
            "message": "OTP verification successful."
        }
    else:
        return {
            "authenticated": False,
            "status": "failed",
            "message": "The entered OTP is incorrect."
        }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
