"""FastAPI gateway server for LINE WORKS bot webhook and API integration."""

import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
import jwt
import requests

# Load environment variables
load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("LINEWORKS_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINEWORKS_CLIENT_SECRET")
BOT_ID = os.getenv("LINEWORKS_BOT_ID")

# Service account ID
SERVICE_ACCOUNT_ID = "vpvtr.serviceaccount@works-2176857"

# Allowed user ID list
ALLOWED_USER_IDS = ["274f2290-478e-4a53-1ae1-04d4998464dd"]

# Production Notion portfolio URL
PORTFOLIO_URL = "https://lopsided-nutmeg-6c7.notion.site/LSI-Python-3fe8a4bb9b5a80b19374ca33a2ae1e27"


@app.get("/")
def health_check():
    """Health check endpoint to verify server status."""
    return {"status": "running", "message": "LINE WORKS Gateway is active."}


@app.post("/webhook")
async def receive_webhook(request: Request):
    """Receive and process webhook events from LINE WORKS."""
    body = await request.json()
    print("Received Webhook Event:", body)

    try:
        source = body.get("source", {})
        user_id = source.get("userId")

        content = body.get("content", {})
        text = content.get("text", "")

        if not user_id:
            return {"status": "ignored"}

        # 1. Check if user ID is included in the allowed list
        if user_id in ALLOWED_USER_IDS:
            reply_text = (
                "認証成功しました！以下のURLからNotionポートフォリオへアクセスできます。\n"
                f"{PORTFOLIO_URL}"
            )
        else:
            reply_text = "申し訳ありません。このBotを利用する権限がありません。"

        # 2. Send reply back to LINE WORKS (call message sending API)
        send_message_to_lineworks(user_id, reply_text)

    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"status": "success"}


def get_line_works_token() -> str:
    """Generate JWT (RS256 signature) and retrieve an access token for LINE WORKS Server API."""
    issued_at = int(time.time())
    expiration = issued_at + 3600  # Valid for 1 hour

    # Create JWT payload
    payload = {
        "iss": CLIENT_ID,
        "sub": SERVICE_ACCOUNT_ID,
        "iat": issued_at,
        "exp": expiration,
    }

    # Load private key file placed in the root folder
    key_filename = "private_20261022112215.key"
    if not os.path.exists(key_filename):
        raise HTTPException(
            status_code=500,
            detail=f"Private key file not found: {key_filename}",
        )

    with open(key_filename, "r", encoding="utf-8") as f:
        private_key = f.read()

    # Sign with RS256 algorithm
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    if isinstance(encoded_jwt, bytes):
        encoded_jwt = encoded_jwt.decode("utf-8")

    # Access token issue request
    token_url = "https://auth.worksmobile.com/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": encoded_jwt,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "bot",
    }

    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code != 200:
        print(f"Failed to get token: {response.text}")
        raise HTTPException(
            status_code=500, detail="Failed to authenticate with LINE WORKS"
        )

    token_json = response.json()
    return token_json.get("access_token")


def send_message_to_lineworks(user_id: str, text: str):
    """Send a message to a user using the LINE WORKS Bot API."""
    access_token = get_line_works_token()

    # Message sending API endpoint (for 1:1 chat)
    url = f"https://www.worksapis.com/v1.0/bots/{BOT_ID}/users/{user_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Sending body (text format)
    payload = {"content": {"type": "text", "text": text}}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        print(f"Successfully sent message to {user_id}")
    else:
        print(f"Failed to send message: {response.status_code}, {response.text}")