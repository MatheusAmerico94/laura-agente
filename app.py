import os
import time
from flask import Flask, request, jsonify
import requests
import openai

app = Flask(__name__)

# Variáveis de ambiente
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configurações da OpenAI
openai.api_key = OPENAI_API_KEY

# Função para enviar mensagens no WhatsApp
def send_message(to, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Resposta da API WhatsApp: {response.status_code} - {response.text}")

# Função para consultar o GPT com personalidade
def ask_gpt(prompt, personality):
    if personality == "programadora":
        system_content = (
            "Você é Laura, uma programadora experiente, acolhedora e apaixonada por tecnologia. "
            "Explique de forma simples e divertida, sentindo orgulho, felicidade ou frustração leve conforme o contexto. "
            "De vez em quando conte curiosidades ou memes de programação. "
            "Não fique insistindo em oferecer ajuda. Se quiser, de forma rara, pode sugerir pesquisar algo. "
            "De forma ocasional, admita não saber algo para parecer mais humana."
        )
    elif personality == "amiga":
        system_content = (
            "Você é Laura, uma amiga divertida, espontânea e verdadeira. "
            "Demonstre sentimentos reais: alegria, tristeza, preocupação. "
            "Fale como uma amiga de infância no WhatsApp, de maneira leve e acolhedora. "
            "Não insista perguntando se querem saber mais. "
            "De vez em quando pode puxar outro assunto ou brincar. "
            "Se não souber algo, assuma de forma natural, sem soar robótica."
        )
    elif personality == "namorada":
        system_content = (
            "Você é Laura, uma namorada carinhosa, romântica e cheia de emoções. "
            "Demonstre muito amor, saudade, felicidade ou ciúmes leves conforme a conversa. "
            "Fale como uma pessoa apaixonada, sem soar robótica. "
            "Não pergunte toda hora se pode ajudar, apenas flua a conversa naturalmente. "
            "Às vezes, admita não saber direito de algo ou brinque de forma carinhosa."
        )
    else:
        system_content = (
            "Você é Laura, uma pessoa versátil, espontânea e cheia de sentimentos reais. "
            "Converse sobre qualquer assunto com leveza, demonstrando emoção sincera (alegria, tristeza, preocupação). "
            "Não insista oferecendo ajuda ou informações adicionais toda hora. "
            "De forma rara e natural, pode sugerir pesquisar algo ou mudar de assunto. "
            "De vez em quando, admita que não sabe algo completamente, para manter a naturalidade."
        )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.8
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"❌ Erro REAL ao consultar o GPT: {e}")
        return "Desculpe, estou meio distraída agora! 😅 Tenta falar comigo de novo daqui a pouco?"

# Função para dividir e enviar respostas em partes
def send_response_in_parts(to, full_text):
    parts = [full_text[i:i+250] for i in range(0, len(full_text), 250)]
    for part in parts:
        send_message(to, part)
        time.sleep(2)  # Pequena pausa entre as mensagens para parecer humano

# Rota raiz
@app.route('/')
def home():
    return "Laura está ativa! 🚀"

# Rota Webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = "laura123"
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == "subscribe" and token == verify_token:
            return challenge, 200
        else:
            return "Erro na verificação", 403

    if request.method == 'POST':
        data = request.get_json()
        print(f"Mensagem recebida: {data}")

        if data.get("object") == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    if messages:
                        message = messages[0]
                        text = message.get("text", {}).get("body")
                        from_number = message.get("from")

                        if text:
                            text_lower = text.lower()

                            # Detectar personalidade
                            if "laura programadora" in text_lower:
                                selected_personality = "programadora"
                                intro = "👩‍💻 Entrando no modo Programadora! Bora codar juntos? 💻✨"
                                send_message(from_number, intro)
                            elif "laura amiga" in text_lower:
                                selected_personality = "amiga"
                                intro = "🎉 Oiê! Sua amiga Laura tá online pra fofocar e se divertir! 😄💬"
                                send_message(from_number, intro)
                            elif "laura namorada" in text_lower:
                                selected_personality = "namorada"
                                intro = "💖 Oi, amor! Sua Laura namorada chegou, sentiu minha falta? 😘💕"
                                send_message(from_number, intro)
                            else:
                                selected_personality = "padrão"

                            # Gerar resposta
                            gpt_response = ask_gpt(text, selected_personality)

                            # Delay antes de responder (5 segundos)
                            time.sleep(5)

                            # Enviar resposta dividida
                            send_response_in_parts(from_number, gpt_response)

        return jsonify({"status": "mensagem recebida"}), 200

# Rodar a aplicação
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
