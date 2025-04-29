from flask import Flask, request, jsonify
import os
import requests
import openai

app = Flask(__name__)

# Tokens e configurações a partir de variáveis de ambiente
VERIFY_TOKEN = "laura123"
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
openai.api_key = os.environ.get("OPENAI_API_KEY")  # OpenAI de forma segura

@app.route("/", methods=["GET"])
def home():
    return "Laura GPT está online! 🚀", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Validação do Webhook no Facebook Developer
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
        # Comunicação com a OpenAI GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Ou "gpt-4" se quiser depois
            messages=[
                {"role": "system", "content": "Você é a Laura, uma assistente virtual divertida, simpática e muito inteligente!"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Erro ao consultar o GPT: {e}")
        return "Desculpe, estou com dificuldades para pensar agora 😅. Pode tentar novamente?"

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
    try:
        response = requests.post(url, headers=headers, json=payload)
