"""
Testaa Simple Trading Solutions signaalia
"""
import requests
import json

def test_signal(signal_text):
    webhook_url = 'http://127.0.0.1:8000/discord-webhook/'
    
    try:
        response = requests.post(
            webhook_url,
            json={'content': signal_text},
            headers={'Content-Type': 'application/json'}
        )
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print(f'SUCCESS! Signal ID: {result["signal_id"]}')
            print('Trade will open automatically in MT5!')
            print('Check Dashboard: http://127.0.0.1:8000/dashboard/')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'Error: {e}')

# Simple Trading Solutions signaali:
discord_message = """Trade READY on AUDUSD!
BUY @ 0.65285 OR SELL @ 0.65246

Buy Trade Parameters:
Entry: 0.65285
SL: 3.9 PIPS - 0.65246
TP1: 3.9 PIPS - 0.65324
TP2: 7.8 PIPS - 0.65363
TP3: 11.7 PIPS - 0.65402

Sell Trade Parameters:
Entry: 0.65246
SL: 3.9 PIPS - 0.65285
TP1: 3.9 PIPS - 0.65207
TP2: 7.8 PIPS - 0.65168
TP3: 11.7 PIPS - 0.65129

Results: Mixed Signals, Slight Bullish Bias with Strong Momentum (4/6 Confirmations)
Status: WAITING FOR BREAKOUT
Recommended Action: Buy"""

print("Testing Simple Trading Solutions signal...")
print(f"Signal: {discord_message[:100]}...")
test_signal(discord_message)