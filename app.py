from flask import Flask, request, jsonify
import os
import requests
import openai

app = Flask(__name__)

# Configurações: puxando variáveis de ambiente
VERIFY_TOKEN = "laura123"
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Laura GPT-4-turbo está online! 🚀", 200

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
            model="gpt-4-turbo",  # ✅ Agora usando gpt-4-turbo
            messages=[
                {"role": "system", "content": "Você é a Laura, uma assistente virtual divertida, simpática, educada e muito inteligente! Sempre responde de forma gentil, alegre e com energia positiva."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Erro ao consultar o GPT: {e}")
        return "Desculpe, estou com dificuldade para pensar agora! 😅 Tente de novo mais tarde!"

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
        print(f"Resposta da API WhatsApp: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao enviar mensagem para o WhatsApp: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
