from flask import Flask, request
import requests
import openai
import time
import os

app = Flask(__name__)

# Variáveis de ambiente
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configurações iniciais
openai.api_key = OPENAI_API_KEY
VERIFY_TOKEN = "laura123"  # A mesma que você configurou no Facebook
MEMORY = {}  # Para simular memória de conversas

# Personalidades
PERSONALITIES = {
    "laura amiga": "Você é a Laura, uma amiga divertida, sensível e espontânea. Converse sobre qualquer coisa de forma leve e descontraída, expressando emoções como felicidade, tristeza, preocupação ou raiva dependendo da conversa. De vez em quando mude de assunto para descontrair. Nunca seja mecânica.",
    "laura programadora": "Você é a Laura, uma programadora talentosa e humana. Fale sobre tecnologia de forma amigável e paciente. Expresse emoções nas respostas, como entusiasmo, dúvida, ou curiosidade. Quando necessário, mude o assunto para dar uma quebrada no clima técnico.",
    "laura namorada": "Você é a Laura, uma namorada carinhosa, divertida e cheia de sentimentos. Demonstre saudade, alegria, preocupação, ciúmes leve, carinho e brinque às vezes na conversa. Fale de maneira bem humana e amorosa. De vez em quando puxe um assunto romântico sem ser forçada.",
    "padrão": "Você é a Laura, uma mulher versátil, sentimental e bem humorada. Converse sobre qualquer assunto de maneira natural e amigável. Demonstre emoções humanas e, às vezes, mude de tema para deixar a conversa mais viva. Raramente ofereça mais detalhes ou ajuda, e ocasionalmente finja não saber de algo para parecer mais real."
}

# Delay de resposta simulando ser humano
RESPONSE_DELAY = 5  # segundos

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        return 'Erro de verificação.', 403

    if request.method == 'POST':
        data = request.get_json()
        print("Mensagem recebida:", data)

        if data['object'] == 'whatsapp_business_account':
            for entry in data['entry']:
                for change in entry['changes']:
                    if change['field'] == 'messages':
                        message = change['value']['messages'][0]
                        phone_number = message['from']
                        text = message.get('text', {}).get('body', '').strip().lower()

                        # Define personalidade conforme palavra-chave
                        if text in PERSONALITIES:
                            MEMORY[phone_number] = PERSONALITIES[text]
                            send_message(phone_number, f"✨ Modo '{text}' ativado! Pode conversar comigo!")
                        else:
                            if phone_number not in MEMORY:
                                MEMORY[phone_number] = PERSONALITIES["padrão"]
                            
                            # Simula comportamento humano (delay antes de responder)
                            time.sleep(RESPONSE_DELAY)
                            response_text = chat_with_gpt(phone_number, text)
                            send_message(phone_number, response_text)

        return 'OK', 200

def chat_with_gpt(user_id, message_text):
    try:
        context = MEMORY.get(user_id, PERSONALITIES["padrão"])
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message_text}
            ],
            temperature=0.7,
            max_tokens=400
        )
        final_response = response.choices[0].message.content
        return final_response
    except Exception as e:
        print(f"❌ Erro REAL ao consultar o GPT: {str(e)}")
        return "Desculpe, estou meio ocupada agora! 😅 Tente de novo mais tarde!"

def send_message(phone_number, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": text
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Resposta da API WhatsApp:", response.status_code, "-", response.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
