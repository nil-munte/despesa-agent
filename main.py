from fastapi import FastAPI, Request
from openai import OpenAI
import os
import json
import requests
import re
import unicodedata

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
# USUARIS PERMESOS
# =========================

VALID_USERS = ["nil", "nuria"]

# =========================
# NORMALITZACIÓ
# =========================

def normalize(text: str):
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text

# =========================
# VALIDACIÓ USUARI
# =========================

def contains_valid_user(text: str):
    text = normalize(text)
    return any(user in text for user in VALID_USERS)

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
# VALIDACIÓ ESTRICTA
# =========================

def validate_data(data):
    if not isinstance(data, dict):
        raise ValueError("No JSON")

    if "nom" not in data or "cost" not in data or "motiu" not in data:
        raise ValueError("Falten camps")

    nom = normalize(str(data["nom"]))
    motiu = str(data["motiu"])

    try:
        cost = float(data["cost"])
    except:
        raise ValueError("Cost invàlid")

    if nom not in VALID_USERS:
        raise ValueError("Usuari no vàlid")

    if cost <= 0:
        raise ValueError("Cost invàlid")

    if not motiu.strip():
        raise ValueError("Motiu buit")

    return {
        "nom": nom,
        "cost": cost,
        "motiu": motiu.strip()
    }

# =========================
# LLM
# =========================

def llm_extract(text: str):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
Extreu dades del text.

Regles:
- "nom" ha de ser "nil" o "nuria"
- "cost" és un número
- "motiu" és el concepte

L'ordre pot ser qualsevol.

No inventis dades.
Si no és clar, retorna error.

Retorna NOMÉS JSON:
{"nom": "...", "cost": 0, "motiu": "..."}
"""
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
        # VALIDACIÓ PRÈVIA
        # =========================

        if not contains_valid_user(text):
            send_message(
                chat_id,
                "❌ Usuari no reconegut.\nUsa: nil o nuria"
            )
            return {"ok": True}

        # =========================
        # LLM + VALIDACIÓ
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
        send_message(
            chat_id,
            "❌ No he pogut interpretar la despesa.\nEx: 'dinar 25 nil'"
        )

    return {"ok": True}