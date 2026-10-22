import os
import hmac
import hashlib
import base64
import requests
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("LINEWORKS_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINEWORKS_CLIENT_SECRET")
BOT_ID = os.getenv("LINEWORKS_BOT_ID")
BOT_SECRET = os.getenv("LINEWORKS_BOT_SECRET")

# アクセスを許可するLINE WORKSのユーザーIDリスト（検証用に自身のID等を入れる）
ALLOWED_USER_IDS = ["wo.63361"]  # 例: 管理者や許可されたメンバーのID

@app.get("/")
def health_check():
    return {"status": "running", "message": "LINE WORKS Gateway is active."}

@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    LINE WORKSからのWebhookイベントを受信するエンドポイント
    """
    body = await request.json()
    
    # デバッグ用：受信したイベント内容をコンソールに表示
    print("Received Webhook Event:", body)

    # メッセージ受信イベントかどうかの判定
    # ※LINE WORKSの仕様に応じたイベント構造をここでハンドリングします
    try:
        source = body.get("source", {})
        user_id = source.get("userId")
        
        # 簡易的なメッセージ内容の取得
        content = body.get("content", {})
        text = content.get("text", "")

        if not user_id:
            return {"status": "ignored"}

        # 1. ユーザーIDが許可リストに含まれているかチェック
        if user_id in ALLOWED_USER_IDS:
            reply_text = "認証成功しました！以下のURLからNotionポートフォリオへアクセスできます。\nhttps://www.notion.so/your-portfolio-link"
        else:
            reply_text = "申し訳ありません。このBotを利用する権限がありません。"

        # 2. LINE WORKSへ返信（メッセージ送信APIの呼び出し）
        send_message_to_lineworks(user_id, reply_text)

    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"status": "success"}

def send_message_to_lineworks(user_id: str, text: str):
    """
    LINE WORKSのBot APIを使ってユーザーにメッセージを送信する関数
    """
    # 実際にはアクセストークンを発行してAPIリクエストを投げます
    # （※詳細はトークン発行ロジックをここに組み込みます）
    print(f"Sending message to {user_id}: {text}")