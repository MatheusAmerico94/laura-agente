from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = "laura123"
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

@app.route("/", methods=["GET"])
def home():
    return "Laura está online!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        return "Token inválido", 403

    if request.method == "POST":
        data = request.get_json()
        if data.get("entry"):
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change.get("value", {})
                    if "messages" in value:
                        for message in value["messages"]:
                            text = message.get("text", {}).get("body", "").lower().strip()
                            from_number = message.get("from")
                            if text == "oi":
                                send_message(from_number, "Oi! 😄 Que bom que você me chamou! Eu sou a Laura! Como posso te ajudar hoje?")
        return jsonify({"status": "mensagem recebida"}), 200

def send_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Resposta da API: {response.status_code} - {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
