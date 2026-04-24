# 💸 Bot de Telegram per gestió de despeses de parella

Aplicació basada en un bot de Telegram que permet registrar despeses en llenguatge natural i calcular balanços entre dues persones.

## 🚀 Objectiu

Permetre registrar despeses de forma ràpida via Telegram, amb:

* Entrada en llenguatge natural
* Processament amb LLM
* Emmagatzematge en Google Sheets
* Càlcul automàtic de balanços

---

## 🧩 Estat actual

✅ Fase 1 completada:

* Bot Telegram funcional via webhook
* Backend desplegat a Render
* Resposta automàtica: `"OK: missatge rebut"`

---

## 🏗 Arquitectura

1. Telegram Bot
2. Backend (FastAPI)
3. LLM via API (fases futures)
4. Google Sheets (fases futures)

---

## ⚙️ Stack tecnològic

* Python
* FastAPI
* Telegram Bot API
* Render (hosting)

---

## 📁 Estructura del projecte

```
projecte/
 ├── main.py
 ├── requirements.txt
 └── README.md
```

---

## 🔧 Configuració

### 1. Crear bot de Telegram

Utilitza BotFather per obtenir el token.

### 2. Variables d'entorn

```
TELEGRAM_TOKEN=el_teu_token
```

---

## ☁️ Deploy (Render)

* Build command:

```
pip install -r requirements.txt
```

* Start command:

```
uvicorn main:app --host 0.0.0.0 --port 10000
```

---

## 🔗 Configurar webhook

```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=<URL>/webhook
```

---

## ✅ Test

Enviar un missatge al bot:

Resposta esperada:

```
OK: missatge rebut
```

---

## 🧪 Debug

Consultar estat webhook:

```
https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

---

## 🗺 Roadmap

* [x] Fase 1: Bot funcional
* [ ] Fase 2: Processament backend
* [ ] Fase 3: Integració LLM
* [ ] Fase 4: Validació dades
* [ ] Fase 5: Google Sheets
* [ ] Fase 6: Respostes intel·ligents
* [ ] Fase 7: Balanços
* [ ] Fase 8: Comanda /balanc

---

## ⚠️ Notes

* El servei pot entrar en mode sleep al free tier de Render
* El webhook es reactivarà automàticament amb noves peticions

---

## 📌 MVP

Objectiu: sistema usable amb cost zero i UX simple

---
