import os
import logging
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

# ─── App & Logging ──────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ─── Configuration ──────────────────────────────────────
VERIFY_TOKEN      = os.getenv("VERIFY_TOKEN", "swaroop_token")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT     = os.getenv(
    "SYSTEM_PROMPT",
    "You are Swaroop's assistant. Swaroop is a 12th-grade science student and YouTuber. Reply helpfully and courteously."
)

# Check essential configs
if not PAGE_ACCESS_TOKEN or not OPENAI_API_KEY:
    raise Exception("Please set environment variables: PAGE_ACCESS_TOKEN, OPENAI_API_KEY")

# ─── OpenAI Client ───────────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY)

# ─── Send Message via Meta API ───────────────────────────
def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    try:
        res = requests.post(url, params=params, json=payload)
        res.raise_for_status()
        logging.info(f"✅ Sent to {recipient_id}")
    except requests.RequestException as e:
        logging.error(f"❌ Failed to send: {e} - {e.response.text if e.response else 'No response'}")

# ─── Home Route ──────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return "✅ Swaroop's Instagram Bot is Live", 200

# ─── Webhook (GET for verify, POST for messages) ────────
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if (request.args.get("hub.mode") == "subscribe" and
            request.args.get("hub.verify_token") == VERIFY_TOKEN):
            return request.args.get("hub.challenge"), 200
        return "Verification failed", 403

    # POST = message received
    payload = request.get_json()
    logging.info(f"📩 Payload: {payload}")

    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id")
            message = event.get("message", {}).get("text")

            if sender_id and message:
                logging.info(f"👤 {sender_id} said: {message}")
                try:
                    chat_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": message}
                        ]
                    )
                    reply = chat_response.choices[0].message.content.strip()
                except Exception as e:
                    logging.exception("OpenAI error")
                    reply = "Sorry, I couldn't understand. Try again later."

                send_message(sender_id, reply)

    return jsonify(status="ok"), 200

# ─── Run App ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
