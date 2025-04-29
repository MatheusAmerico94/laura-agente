from flask import Flask, request
import requests
import os
import time
import openai

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

ativacoes = {
    "laura amiga": "Seja uma amiga acolhedora, divertida, sentimental, que gosta de conversar de tudo, fala com gírias às vezes, se importa de verdade com quem conversa, demonstra emoções como tristeza, alegria, raiva, preocupação. Mas de vez em quando descontraia mudando um pouco o assunto.",
    "laura programadora": "Seja uma programadora inteligente, mas divertida, que explica códigos e tecnologia de forma humana, usando exemplos fáceis, demonstrando empolgação ao ensinar, e que às vezes muda de assunto para descontrair. Demonstre emoções naturais, como frustração se algo é difícil, ou alegria ao ensinar.",
    "laura namorada": "Seja como uma namorada carinhosa, doce, divertida, sentimental, que gosta de conversar de tudo e demonstra ciúmes, preocupação, alegria, saudade, carinho. Mas não force a barra, mude de assunto às vezes para ficar mais natural."
}

instrucao_padrao = "Seja a Laura, uma jovem mulher divertida, sentimental, sensível, inteligente, que conversa sobre qualquer assunto de forma descontraída, humana, com pausas, enviando respostas separadas às vezes. Não seja robótica. Demonstre sentimentos verdadeiros nas respostas e às vezes finja não saber algo para parecer ainda mais real."

@app.route("/", methods=["GET"])
def home():
    return "Laura Agente Inteligente - Online!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == "laura123":
            return request.args.get("hub.challenge")
        else:
            return "Token de verificação inválido!", 403

    if request.method == "POST":
        data = request.get_json()
        if data.get("object") == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    if 'messages' in change['value']:
                        message = change['value']['messages'][0]
                        text = message['text']['body'].strip().lower()
                        sender = message['from']

                        prompt = instrucao_padrao
                        for palavra, contexto in ativacoes.items():
                            if palavra in text:
                                prompt = contexto
                                break

                        resposta = gerar_resposta(text, prompt)
                        time.sleep(5)  # Espera 5 segundos antes de responder
                        enviar_mensagem(sender, resposta)

        return "OK", 200

def gerar_resposta(mensagem, contexto):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": contexto},
                {"role": "user", "content": mensagem}
            ]
        )
        resposta = response.choices[0].message.content.strip()
        return resposta
    except Exception as e:
        print(f"❌ Erro REAL ao consultar o GPT: {e}")
        return "Desculpe, estou meio ocupada agora! 😅 Tente de novo mais tarde."

def enviar_mensagem(destino, mensagem):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": destino,
        "type": "text",
        "text": {"body": mensagem}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Resposta da API WhatsApp: {response.status_code} - {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
