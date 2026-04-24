from fastapi import FastAPI, Request
from openai import OpenAI
import os
import json
import requests
import re
import unicodedata
from difflib import get_close_matches

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
# USUARIS (CANÒNICS + ALIASES)
# =========================

USERS = {
    "nil": ["nil", "Nil"],
    "nuria": ["nuria", "núria", "Nuria", "Núria"]
}

# =========================
# NORMALITZACIÓ
# =========================

def normalize(text: str):
    text = text.lower().strip()

    # treure accents
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    return text

# =========================
# DETECCIÓ USUARI
# =========================

def extract_user(text: str):
    text = normalize(text)

    for canonical, aliases in USERS.items():
        for alias in aliases:
            if alias in text:
                return canonical

    # fuzzy fallback (errors petits)
    all_users = list(USERS.keys())
    match = get_close_matches(text, all_users, n=1, cutoff=0.6)

    if match:
        return match[0]

    return None

# =========================
# INPUT INCOMPLET
# =========================

def is_incomplete(text: str):
    has_number = any(c.isdigit() for c in text)
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
                "❌ No reconec l'usuari.\nUsa: nil, anna o nuria"
            )
            return {"ok": True}

        # =========================
        # LLM
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