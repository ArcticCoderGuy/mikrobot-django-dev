"""
Hae Telegram Chat ID
Auttaa löytämään oikean chat ID:n viestien lähettämistä varten
"""

import requests
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_telegram_updates():
    """Hae bot updates ja näytä chat ID:t"""
    
    bot_token = "8139279606:AAFay9O4LDPQTRQQ6jjaDWeQxqeOmfoapi0"
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    print("🔍 Haetaan Telegram-päivityksiä...")
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['ok']:
                updates = data.get('result', [])
                
                if not updates:
                    print("\n❌ Ei viestejä!")
                    print("1. Mene Telegramiin")
                    print("2. Etsi @Mkapriobot")
                    print("3. Paina START")
                    print("4. Lähetä viesti: Hello")
                    print("5. Aja tämä skripti uudelleen")
                    return
                
                print(f"\n✅ Löydettiin {len(updates)} viestiä")
                print("\n📱 Chat ID:t:")
                print("-" * 50)
                
                seen_chats = set()
                
                for update in updates:
                    message = update.get('message', {})
                    chat = message.get('chat', {})
                    from_user = message.get('from', {})
                    
                    chat_id = chat.get('id')
                    chat_type = chat.get('type', 'unknown')
                    username = from_user.get('username', 'N/A')
                    first_name = from_user.get('first_name', '')
                    
                    if chat_id and chat_id not in seen_chats:
                        seen_chats.add(chat_id)
                        print(f"\n📍 Chat ID: {chat_id}")
                        print(f"   Tyyppi: {chat_type}")
                        print(f"   Käyttäjä: @{username} ({first_name})")
                        print(f"   Viesti: {message.get('text', 'N/A')[:50]}...")
                
                print("\n" + "-" * 50)
                print(f"💡 Käytä Chat ID:tä telegram_notifier.py:ssä:")
                print(f'   self.chat_id = chat_id or "{list(seen_chats)[0]}"')
                
            else:
                print(f"❌ API virhe: {data}")
        else:
            print(f"❌ HTTP virhe: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Virhe: {e}")

if __name__ == "__main__":
    print("🤖 MikroBot Telegram Chat ID Finder")
    print("=" * 50)
    print("HUOM: Sinun täytyy lähettää viesti @Mkapriobot:lle ensin!")
    print("=" * 50)
    
    get_telegram_updates()