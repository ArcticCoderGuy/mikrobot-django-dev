"""
Testa täysi end-to-end automaatio:
1. Lähetä Simple Trading Solutions signaali webhookiin
2. Tarkista että signaali tallentuu tietokantaan
3. Tarkista että kauppa avautuu MT5:ssä
4. Tarkista että kauppa näkyy dashboardissa
"""
import requests
import json
import time
import sys
import os

# Add Django settings
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')

import django
django.setup()

from signals.models import MQL5Signal
from trading.models import Trade
import MetaTrader5 as mt5

def test_full_automation():
    print("=== TESTING FULL AUTOMATION ===")
    
    # Step 1: Send signal to webhook
    webhook_url = 'http://127.0.0.1:8000/discord-webhook/'
    test_signal = """Trade READY on EURUSD!
BUY @ 1.08500 OR SELL @ 1.08450

Buy Trade Parameters:
Entry: 1.08500
SL: 3.9 PIPS - 1.08450
TP1: 3.9 PIPS - 1.08550
TP2: 7.8 PIPS - 1.08580
TP3: 11.7 PIPS - 1.08620

Sell Trade Parameters:
Entry: 1.08450
SL: 3.9 PIPS - 1.08500
TP1: 3.9 PIPS - 1.08410
TP2: 7.8 PIPS - 1.08380
TP3: 11.7 PIPS - 1.08340

Results: Strong Buy Signal (5/6 Confirmations)
Status: CONFIRMED SIGNAL
Recommended Action: Buy"""
    
    print("1. Sending signal to webhook...")
    try:
        response = requests.post(
            webhook_url,
            json={'content': test_signal},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Signal sent! ID: {result['signal_id']}")
            signal_id = result['signal_id']
        else:
            print(f"   ERROR: Webhook failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ERROR: Error sending signal: {e}")
        return False
    
    # Step 2: Check database
    print("2. Checking database...")
    time.sleep(2)  # Wait for processing
    
    try:
        signal = MQL5Signal.objects.get(id=signal_id)
        print(f"   SUCCESS: Signal found in database: {signal.symbol} {signal.direction}")
        print(f"   Status: {signal.status}")
        print(f"   Entry: {signal.entry_price}, SL: {signal.stop_loss}, TP: {signal.take_profit}")
    except MQL5Signal.DoesNotExist:
        print("   ERROR: Signal not found in database!")
        return False
    
    # Step 3: Check if trade was executed
    print("3. Checking trade execution...")
    time.sleep(3)  # Wait for MT5 execution
    
    # Refresh signal from database
    signal.refresh_from_db()
    print(f"   Signal status after execution: {signal.status}")
    
    if signal.status == 'executed':
        print("   SUCCESS: Signal marked as executed!")
        
        # Check Trade record
        try:
            trade = Trade.objects.filter(signal=signal).first()
            if trade:
                print(f"   Trade record created: Ticket {trade.mt5_ticket}")
                print(f"   Trade status: {trade.status}")
            else:
                print("   WARNING: No Trade record found")
        except Exception as e:
            print(f"   ERROR: Error checking trade record: {e}")
    
    elif signal.status == 'failed':
        print(f"   ERROR: Signal execution failed: {signal.rejection_reason}")
        return False
    else:
        print(f"   PROCESSING: Signal still processing (status: {signal.status})")
    
    # Step 4: Check MT5 directly
    print("4. Checking MT5 positions...")
    try:
        if not mt5.initialize():
            print("   ERROR: Failed to initialize MT5")
            return False
        
        positions = mt5.positions_get()
        if positions:
            print(f"   INFO: Found {len(positions)} open positions in MT5:")
            for pos in positions:
                if pos.comment and str(signal_id)[:8] in pos.comment:
                    print(f"   TARGET: FOUND OUR TRADE! Ticket: {pos.ticket}")
                    print(f"      Symbol: {pos.symbol}, Type: {'BUY' if pos.type == 0 else 'SELL'}")
                    print(f"      Volume: {pos.volume}, Entry: {pos.price_open}")
                    print(f"      Current P&L: {pos.profit}")
                    return True
            
            print("   WARNING: Positions found but none match our signal")
            for pos in positions[:3]:  # Show first 3
                print(f"      - {pos.symbol} {'BUY' if pos.type == 0 else 'SELL'} {pos.volume} (Comment: {pos.comment})")
        else:
            print("   INFO: No open positions in MT5")
    
    except Exception as e:
        print(f"   ERROR: Error checking MT5: {e}")
    finally:
        mt5.shutdown()
    
    # Step 5: Check dashboard API
    print("5. Checking dashboard API...")
    try:
        response = requests.get('http://127.0.0.1:8000/dashboard/api/live-data/')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                trades = data['data']['trades']
                sts_signals = data['data'].get('sts_signals', [])
                
                print(f"   INFO: Dashboard shows {len(trades)} active trades")
                print(f"   INFO: Dashboard shows {len(sts_signals)} STS signals")
                
                # Find our signal
                our_signal = None
                for sig in sts_signals:
                    if str(sig['id']) == str(signal_id):
                        our_signal = sig
                        break
                
                if our_signal:
                    print(f"   SUCCESS: Our signal found in dashboard!")
                    print(f"      Status: {our_signal['status']}")
                else:
                    print("   WARNING: Our signal not in dashboard STS signals")
            else:
                print("   ERROR: Dashboard API returned error")
        else:
            print(f"   ERROR: Dashboard API failed: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: Error checking dashboard: {e}")
    
    print("\n=== TEST COMPLETED ===")
    return signal.status == 'executed'

if __name__ == "__main__":
    success = test_full_automation()
    if success:
        print("SUCCESS: FULL AUTOMATION WORKING! Trade was executed automatically!")
    else:
        print("ERROR: Automation not fully working yet. Check the issues above.")