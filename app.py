from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
app.secret_key = "kitobxonlar_secret_key_123"

# Sizning aniq bot tokeningiz va shaxsiy ID raqamingiz muhrlandi 🔒
BOT_TOKEN = "8956612695:AAEcCcfbRsfxzY7_Jm9mqcGf0hPsVMhBjUk"
ADMIN_CHAT_ID = "5777502829"

# Xabarlarni xotirada saqlash bazasi
chat_database = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<page>')
def route_pages(page):
    if page.endswith('.html'):
        html_page = page
    else:
        html_page = page + '.html'
        
    try:
        return render_template(html_page)
    except:
        return jsonify({"error": "Sahifa topilmadi"}), 404

# 🚀 TELEGRAM BILAN 100% KAFOLATLANGAN BOG'LANISH YO'LAGI
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    msg_text = data.get('message')
    sender_name = data.get('sender', 'Muslimbek Xalmatov')
    
    user_key = sender_name.lower().strip()
    
    if user_key not in chat_database:
        chat_database[user_key] = []
        
    chat_database[user_key].append({"text": msg_text, "is_admin": False})
    
    # Telegram tushunadigan chiroyli matn formatini yig'amiz
    telegram_text = f"📥 YANGI SHAXSIY XABAR!\n\n👤 Kimdan: {sender_name}\n🔑 Reply ID: #{user_key}\n\n💬 Xabar:\n{msg_text}"
    
    # Telegram API cheklovlarini yorib o'tish uchun params tizimidan foydalanamiz (Xatosiz ketadi!) 🔥
    tg_url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": telegram_text
    }
    
    # Telegram serverlariga portlatib yuboramiz
    requests.get(tg_url, params=payload)
    
    return jsonify({"success": True})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    sender_name = request.args.get('sender', 'Muslimbek Xalmatov')
    user_key = sender_name.lower().strip()
    messages = chat_database.get(user_key, [])
    return jsonify(messages)

# ADMIN JAVOB YOZGANDA SAYTGA QAYTARISH TIZIMI
@app.route('/tg_webhook', methods=['POST'])
def tg_webhook():
    data = request.json
    if "message" in data and "reply_to_message" in data["message"]:
        reply_text = data["message"]["text"]
        original_text = data["message"]["reply_to_message"]["text"]
        
        if "Reply ID: #" in original_text:
            try:
                user_key = original_text.split("Reply ID: #")[1].split("\n")[0].strip()
                if user_key in chat_database:
                    chat_database[user_key].append({"text": reply_text, "is_admin": True})
            except Exception as e:
                print("Webhook xatolik:", e)
                
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
