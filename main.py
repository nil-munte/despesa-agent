from fastapi import FastAPI, Request
from openai import OpenAI
import os
import json
import requests
import re

app = FastAPI()

# =========================
# CONFIG
# =========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# =========================
# USUARIS
# =========================

USERS = ["nil", "anna"]

# =========================
# UX HELPERS
# =========================

def extract_user(text: str):
    text_lower = text.lower()

    for user in USERS:
        if user in text_lower:
            return user

    # fuzzy simple
    for user in USERS:
        if user[:3] in text_lower:
            return user

    return None


def is_incomplete(text: str):
    has_number = any(char.isdigit() for char in text)
    has_words = len(text.split()) >= 2
    return not (has_number and has_words)

# =========================
# JSON SAFE PARSE
# =========================

def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Invalid JSON")

# =========================
# VALIDACIÓ
# =========================

def validate_data(data):
    nom = data.get("nom", "desconegut")
    motiu = data.get("motiu", "sense motiu")

    try:
        cost = float(data.get("cost", 0))
    except:
        cost = 0

    return {
        "nom": nom,
        "cost": cost,
        "motiu": motiu
    }

# =========================
# LLM (GROQ)
# =========================

def llm_extract(text: str):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ets un extractor de despeses d'una parella. "
                    "Retorna NOMÉS JSON amb: nom, cost, motiu. "
                    "No inventis dades. "
                    "nom ha de ser un usuari conegut."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0
    )

    raw = response.choices[0].message.content

    parsed = safe_json_parse(raw)
    return validate_data(parsed)

# =========================
# TELEGRAM
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

    try:
        message = data.get("message", {})
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        print("📩 Input:", text)

        # =========================
        # UX 1: input incomplet
        # =========================
        if is_incomplete(text):
            send_message(
                chat_id,
                "🤔 No ho he entès del tot.\nEx: dinar 25 nil"
            )
            return {"ok": True}

        # =========================
        # UX 2: usuari desconegut
        # =========================
        user = extract_user(text)

        if user is None:
            send_message(
                chat_id,
                "❌ No reconec l'usuari.\nUsa: nil o anna"
            )
            return {"ok": True}

        # =========================
        # LLM PROCESSING
        # =========================
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
        send_message(chat_id, "Error processant missatge 😅")

    return {"ok": True}