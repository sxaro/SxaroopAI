# ✅ Sxaroop ChatGPT Instagram Bot

from flask import Flask, request
import openai
import requests
import os

app = Flask(__name__)

# 🔐 Secure tokens from environment
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")  # e.g. swaroop_token
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ✅ Meta reply function
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    print("📤 Sent to Meta:", response.status_code, response.text)

# ✅ Home route for Render health check
@app.route("/")
def home():
    return "✅ Swaroop ChatGPT Bot is Running!"

# ✅ Webhook route for Meta verification + message processing
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("🔐 Webhook verified")
            return challenge, 200
        return "❌ Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("📩 Incoming data:", data)

        try:
            message_event = data['entry'][0]['messaging'][0]
            sender_id = message_event['sender']['id']
            user_message = message_event['message']['text']
            print(f"👤 User: {sender_id} ➡️ {user_message}")

            # 🔁 Get ChatGPT reply
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": user_message}]
            )
            bot_reply = response.choices[0].message.content.strip()
            print("🤖 Bot reply:", bot_reply)

            # 📤 Send message back
            send_message(sender_id, bot_reply)

        except Exception as e:
            print("❌ Error:", e)

        return "ok", 200

# ✅ Run app for local testing (Render uses gunicorn)
if __name__ == "__main__":
    app.run()
