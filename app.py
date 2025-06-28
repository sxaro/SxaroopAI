# Sxaroop AI BOT

from flask import Flask, request
import openai
import requests

app = Flask(__name__)

# 🔐 Tokens (ye baad me Render ke ENV variables me daloge)
VERIFY_TOKEN = "swaroop_token"
PAGE_ACCESS_TOKEN = "YOUR_META_PAGE_ACCESS_TOKEN"
openai.api_key = "YOUR_OPENAI_API_KEY"

# ✅ Reply bhejne ka function (Meta Send API)
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, headers=headers, json=payload)

# ✅ Basic health route
@app.route("/")
def home():
    return "✅ Swaroop ChatGPT Bot is Running!"

# ✅ Webhook for Meta
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "❌ Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        try:
            message_event = data['entry'][0]['messaging'][0]
            sender_id = message_event['sender']['id']
            user_message = message_event['message']['text']

            # ChatGPT se reply lo
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": user_message}]
            )
            bot_reply = response.choices[0].message.content.strip()

            # Reply user ko bhejo
            send_message(sender_id, bot_reply)

        except Exception as e:
            print("❌ Error:", e)

        return "ok", 200

# ✅ Render ko run karne ke liye zaroori
if __name__ == "__main__":
    app.run()
