# 🤖 Agent Guide — Bot de Despeses

Aquest document defineix com treballar sobre el projecte de forma incremental i segura.

---

## 🎯 Principi clau

⚠️ **No avançar de fase fins que l’anterior funcioni correctament**

---

## 🧩 Fases del projecte

### Fase 1 — Bot funcional

* Webhook operatiu
* Resposta fixa
* Deploy estable

### Fase 2 — Backend processing

* Lectura del missatge
* Logs correctes

### Fase 3 — LLM parsing

* Text → JSON estructurat
* Sense errors de parsing

### Fase 4 — Validació

* Validació estricta de dades
* Gestió d’errors

### Fase 5 — Persistència

* Integració amb Google Sheets
* Evitar duplicats

### Fase 6 — Respostes

* Confirmació coherent amb dades

### Fase 7 — Balanç

* Càlcul de deutes entre usuaris

### Fase 8 — Comandes

* `/balanc`

---

## 🧠 Decisions tècniques clau

### 1. LLM no és fiable al 100%

Sempre:

* validar output
* fer retry si cal
* no confiar en format perfecte

---

### 2. Model de dades (IMPORTANT)

Evitar ambigüitat:

```
{
  "qui_paga": "Joan",
  "cost": 25,
  "motiu": "sopar"
}
```

Assumir repartiment 50/50 per MVP

---

### 3. Idempotència

Evitar duplicats:

* usar identificador únic per missatge
* tenir en compte retries

---

### 4. Google Sheets ≠ backend

Sheets és:

* storage

Backend és:

* lògica
* càlcul

---

## 🧪 Testing strategy

Cada fase ha de tenir:

* test manual
* criteri d’èxit clar

No avançar si:

* hi ha errors intermitents
* comportament no determinista

---

## 🚨 Errors comuns

* Webhook mal configurat
* JSON del LLM trencat
* Duplicació de dades
* Inputs ambigus

---

## 🔄 Estratègia de desenvolupament

Sempre:

1. Implementar mínim
2. Testar
3. Validar
4. Iterar

Evitar:

* sobreenginyeria
* afegir funcionalitat abans d’hora

---

## 🎯 Objectiu final

Sistema:

* usable diàriament
* robust
* zero cost
* UX ràpida

---

## 🧭 Filosofia

"Simplicitat > perfecció"

---
