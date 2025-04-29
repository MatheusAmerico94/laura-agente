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
        data = request.json
        print("Mensagem recebida:", data)

        if data.get("entry"):
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change["value"]
                    if "messages" in value:
                        messages = value["messages"]
                        for message in messages:
                            text = message.get("text", {}).get("body", "")
                            phone_number = value["metadata"]["phone_number_id"]
                            from_number = message["from"]

                            # Agora o bot ativa com "Oi" (não mais "Américo")
                            if text.lower().strip() == "oi":
                                send_message(from_number, "Oi! 😄 Que bom que você me chamou! Sou a Laura! Como posso te ajudar hoje?")

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
    print("Resposta do envio:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
