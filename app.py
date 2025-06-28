# ✅ Sxaroop AI - Instagram DM ChatGPT Bot

from flask import Flask, request
import requests
import os
from openai import OpenAI

app = Flask(__name__)

# ✅ Environment variables from Render Dashboard
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")             # e.g. swaroop_token
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")   # Meta token
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")         # Your OpenAI Key

# ✅ OpenAI client setup (New SDK)
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Function to send message via Meta API
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

# ✅ Health Check Route
@app.route("/")
def home():
    return "✅ Swaroop AI is Running!"

# ✅ Webhook Route
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

            # ✅ Check if message is present and has text
            if 'message' in message_event and 'text' in message_event['message']:
                user_message = message_event['message']['text']
                print(f"👤 User: {sender_id} ➡️ {user_message}")

                # 🔁 Get GPT reply using new SDK
                # completion = client.chat.completions.create(
                #     model="gpt-3.5-turbo",
                #     messages=[
                #         {"role": "user", "content": user_message}
                #     ]
                # )
                # bot_reply = completion.choices[0].message.content.strip()
                # print("🤖 Bot reply:", bot_reply)
                
                client = OpenAI(
                  api_key="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"
                )
                
                completion = client.chat.completions.create(
                  model="gpt-4o-mini",
                  store=True,
                  messages=[
                    {"role": "user", "content": "write a haiku about ai"}
                  ]
                )
                
                print(completion.choices[0].message);                
                
                # 📤 Send reply back
                send_message(sender_id, bot_reply)
            else:
                print("⚠️ Message has no text — ignored.")

        except Exception as e:
            print("❌ Error:", e)

        return "ok", 200

# ✅ For local testing
if __name__ == "__main__":
    app.run()
