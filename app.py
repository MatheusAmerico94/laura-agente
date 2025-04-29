from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Variável de ambiente para o token de verificação
VERIFY_TOKEN = "laura123"  # Esse é o mesmo que você colocou no Facebook Developer

@app.route("/", methods=["GET"])
def home():
    return "Laura está online!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Facebook mandando o desafio de verificação
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        return "Token inválido", 403

    if request.method == "POST":
        data = request.json
        print("Mensagem recebida:", data)
        # Aqui você pode processar a mensagem recebida (iremos melhorar depois)
        return jsonify({"status": "mensagem recebida"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
