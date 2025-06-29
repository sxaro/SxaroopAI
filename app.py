# TEST CODE
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

# ─── Send Message Function ─────────────
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}

    try:
        res = requests.post(url, json=payload, headers=headers)
        res.raise_for_status()
        logging.info(f"✅ Replied to {recipient_id}")
    except requests.RequestException as e:
        logging.error(f"❌ Failed to send: {e} - {e.response.text if e.response else 'No response'}")

# ─── Home Check ────────────────────────
@app.route("/", methods=["GET"])
def home():
    return "✅ Instagram Auto-Reply Bot is running on Render", 200

# ─── Webhook Verification + Handling ───
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if (request.args.get("hub.mode") == "subscribe" and
            request.args.get("hub.verify_token") == VERIFY_TOKEN):
            return request.args.get("hub.challenge"), 200
        return "Verification failed", 403

    # POST = incoming DM
    payload = request.get_json()
    logging.info(f"📩 Incoming: {payload}")

    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id")
            message = event.get("message", {}).get("text", "")

            if sender_id and message:
                logging.info(f"👤 From {sender_id}: {message}")

                # Reply logic (basic)
                if "hello" in message.lower():
                    reply = "Hi! How can I help you?"
                elif "info" in message.lower():
                    reply = "Swaroop is a 12th-grade science student and YouTuber."
                else:
                    reply = "Thanks for your message! I'll get back to you soon."

                send_message(sender_id, reply)

    return jsonify(status="ok"), 200

# ─── Start Server ──────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
