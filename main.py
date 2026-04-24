from fastapi import FastAPI, Request
from openai import OpenAI
import os
import json
import requests

app = FastAPI()

# =========================
# CONFIGURACIÓ
# =========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# =========================
# LLM (EXTRACCIÓ JSON)
# =========================

def llm_extract(text: str):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ets un extractor de despeses. "
                    "Retorna NOMÉS JSON vàlid amb claus: nom, cost, motiu. "
                    "Sense text extra."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    return json.loads(content)

# =========================
# TELEGRAM SEND MESSAGE
# =========================

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

# =========================
# WEBHOOK
# =========================

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    print("📩 Update rebut:", data)

    try:
        message = data.get("message", {})
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        print("💬 Text:", text)

        # LLM extraction
        result = llm_extract(text)

        resposta = (
            f"📌 Afegit\n"
            f"👤 {result['nom']}\n"
            f"💰 {result['cost']}€\n"
            f"📝 {result['motiu']}"
        )

        send_message(chat_id, resposta)

    except Exception as e:
        print("❌ Error:", e)
        send_message(chat_id, "No he entès el missatge 😅")

    return {"ok": True}