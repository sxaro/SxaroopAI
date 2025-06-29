import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ─── Config ───────────────────────────
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "swaroop_token")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

if not PAGE_ACCESS_TOKEN:
    raise Exception("❌ PAGE_ACCESS_TOKEN is missing!")

# ─── Send Message to Instagram ────────
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
        logging.error(f"❌ Send error: {e}")

# ─── Home ─────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return "✅ Swaroop IG Bot Running (no GPT)", 200

# ─── Webhook ──────────────────────────
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    # POST = message
    data = request.get_json()
    logging.info(f"📩 Incoming: {data}")

    for entry in data.get("entry", []):
        for msg_event in entry.get("messaging", []):
            sender_id = msg_event.get("sender", {}).get("id")
            message = msg_event.get("message", {}).get("text", "").lower()

            if not sender_id or not message:
                continue

            # ─── Keyword-based reply ───
            if "hello" in message:
                reply = "Hey! How can I help you?"
            elif "info" in message:
                reply = "Swaroop is a 12th-grade science student and YouTuber."
            else:
                reply = "Thanks for your message! I’ll get back to you soon."

            send_message(sender_id, reply)

    return jsonify(status="ok"), 200

# ─── Start App ────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
