# ✅ Sxaroop AI - Instagram DM ChatGPT Bot (Improved)

```python
import os
import logging
from flask import Flask, request
from openai import OpenAI, error as openai_error
import requests

# ─── Configuration ───────────────────────────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Environment variables (set these on Render or your host)
VERIFY_TOKEN      = os.getenv("VERIFY_TOKEN")      # e.g. "swaroop_token"
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN") # Meta Page access token
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")    # OpenAI API key
SYSTEM_PROMPT     = os.getenv(
    "SYSTEM_PROMPT",
    "You are Swaroop's assistant. Swaroop is a 12th-grade science student and YouTuber. Reply helpfully and courteously."
)

# Validate configuration
missing = [k for k in ("VERIFY_TOKEN","PAGE_ACCESS_TOKEN","OPENAI_API_KEY") if not globals()[k]]
if missing:
    logging.critical(f"Missing environment vars: {', '.join(missing)}")
    raise SystemExit(f"ERROR: Please set {', '.join(missing)}")

# ─── OpenAI Client ─────────────────────────────────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY)

# ─── Utility: Send Message via Meta Send API ───────────────────────────────────
def send_message(recipient_id: str, message_text: str) -> None:
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    try:
        resp = requests.post(url, params=params, json=payload, timeout=5)
        resp.raise_for_status()
        logging.info(f"Meta Reply ✅ to {recipient_id}: {resp.status_code}")
    except requests.RequestException as e:
        logging.error(f"Meta Reply ❌ to {recipient_id}: {e} | Response: {getattr(e.response, 'text', '')}")

# ─── Health Check ────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return "✅ Swaroop AI Bot is Running!", 200

# ─── Webhook Verification & Message Handler ────────────────────────────────────
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode      = request.args.get("hub.mode")
        token     = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logging.info("Webhook verified successfully")
            return challenge, 200
        logging.warning("Webhook verification failed")
        return "Verification failed", 403

    data = request.get_json(silent=True)
    logging.info(f"📩 Incoming payload: {data}")
    if not data or data.get("object") not in ("page","instagram"):
        return "ignored", 200

    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender = event.get("sender", {}).get("id")
            msg    = event.get("message", {})
            text   = msg.get("text")
            if not sender or not text:
                logging.info("⚠️ No text message to handle, ignoring")
                continue
            logging.info(f"👤 From {sender}: {text}")

            # ─── Call OpenAI ──────────────────────────────────────────────
            try:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": text}
                    ]
                )
                reply = completion.choices[0].message.content.strip()
                logging.info(f"🤖 GPT Reply: {reply}")

            except openai_error.InvalidRequestError as e:
                logging.error(f"OpenAI InvalidRequest: {e}")
                reply = "Sorry, I couldn't process that request."
            except openai_error.AuthenticationError as e:
                logging.error(f"OpenAI Auth Error: {e}")
                reply = "API key error. Please check my configuration."
            except openai_error.RateLimitError as e:
                logging.error(f"OpenAI Rate Limit: {e}")
                reply = "I'm a bit busy right now. Please try again shortly."
            except openai_error.OpenAIError as e:
                logging.error(f"OpenAI General Error: {e}")
                reply = "Oops! Something went wrong on my end."
            except Exception as e:
                logging.exception("Unexpected error calling OpenAI")
                reply = "Unexpected error. Please try again later."

            # ─── Send back via Meta ───────────────────────────────────────
            send_message(sender, reply)

    return "ok", 200

# ─── Entry Point for Local & Render ────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

## requirements.txt
```
flask
requests
openai>=1.0.0
gunicorn
