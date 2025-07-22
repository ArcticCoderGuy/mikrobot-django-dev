"""
Lähetä signaali manuaalisesti Discordista
"""
import requests
import json

def send_signal():
    webhook_url = 'http://127.0.0.1:8000/discord-webhook/'
    
    print("Kopioi signaali Discordista ja liitä tähän:")
    signal_text = input("Signaali: ")
    
    try:
        response = requests.post(
            webhook_url,
            json={'content': signal_text},
            headers={'Content-Type': 'application/json'}
        )
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print(f'✅ Signaali vastaanotettu! ID: {result["signal_id"]}')
            print('💰 Kauppa avataan automaattisesti MT5:ssä!')
        else:
            print(f'❌ Virhe: {response.text}')
    except Exception as e:
        print(f'❌ Virhe: {e}')

if __name__ == "__main__":
    send_signal()