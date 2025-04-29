from flask import Flask, request, jsonify
import os
import requests
import openai

app = Flask(__name__)

# Tokens e configurações puxadas das Variáveis de Ambiente
VERIFY_TOKEN = "laura123"
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Laura GPT está online! 🚀", 200

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
                            text = message.get("text", {}).get("body", "").strip()
                            from_number = message.get("from")
                            gpt_response = ask_gpt(text)
                            send_message(from_number, gpt_response)
        return jsonify({"status": "mensagem recebida"}), 200

def ask_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Ou "gpt-4" se
