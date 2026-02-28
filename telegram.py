import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    """Send a message to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Split into chunks if message too long (Telegram limit 4096 chars)
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    
    for chunk in chunks:
        payload = {
            "chat_id": CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("✅ Telegram message sent!")
            else:
                print(f"❌ Telegram error: {response.text}")
        except Exception as e:
            print(f"❌ Telegram error: {e}")