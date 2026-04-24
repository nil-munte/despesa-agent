from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"


@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    print("📩 Missatge rebut:", data)

    try:
        message = data.get("message", {})
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        print(f"👤 chat_id: {chat_id}")
        print(f"💬 text: {text}")

        send_message(chat_id, f"He rebut: {text}")

    except Exception as e:
        print("❌ Error processant missatge:", e)

    return {"ok": True}


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)