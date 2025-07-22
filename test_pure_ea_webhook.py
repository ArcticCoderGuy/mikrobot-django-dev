"""
Test PURE EA webhook with simulated BOS signal
"""
import requests
import json

def test_pure_ea_webhook():
    print("=== TESTING PURE EA WEBHOOK ===")
    
    # Simulate PURE EA JSON signal (same format as in MQL5 code)
    pure_ea_signal = {
        "ea_name": "MikroBot_BOS",
        "ea_version": "1.04",
        "signal_type": "BOS_RETEST",
        "symbol": "EURUSD",
        "direction": "BUY",
        "trigger_price": 1.08500,
        "h1_bos_level": 1.08450,
        "h1_bos_direction": "BULLISH",
        "m15_break_high": 1.08520,
        "m15_break_low": 1.08480,
        "pip_trigger": 0.6,
        "timestamp": "2025-01-22T17:15:00Z",
        "timeframe": "M15",
        "account": 107033449
    }
    
    webhook_url = "http://127.0.0.1:8000/api/signals/receive/"
    
    print("1. Sending PURE EA signal...")
    print(f"   Symbol: {pure_ea_signal['symbol']}")
    print(f"   Direction: {pure_ea_signal['direction']}")
    print(f"   Trigger Price: {pure_ea_signal['trigger_price']}")
    print(f"   BOS Level: {pure_ea_signal['h1_bos_level']}")
    
    try:
        response = requests.post(
            webhook_url,
            json=pure_ea_signal,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n2. Response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   SUCCESS: PURE EA signal received!")
            print(f"   Signal ID: {result['signal_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            
            return result['signal_id']
        else:
            print(f"   ERROR: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"   ERROR: Invalid JSON response: {e}")
        return None

def check_signal_in_database(signal_id):
    """Check if signal was stored correctly in database"""
    if not signal_id:
        return
        
    print(f"\n3. Checking signal {signal_id} in database...")
    
    import os
    import django
    import sys
    
    # Add Django settings
    sys.path.append('.')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')
    django.setup()
    
    try:
        from signals.models import MQL5Signal
        
        signal = MQL5Signal.objects.get(id=signal_id)
        print(f"   Found signal: {signal.symbol} {signal.direction}")
        print(f"   Source: {signal.source_name}")
        print(f"   EA Name: {signal.ea_name}")
        print(f"   Signal Type: {signal.signal_type}")
        print(f"   Status: {signal.status}")
        print(f"   Entry: {signal.entry_price}")
        print(f"   SL: {signal.stop_loss}")
        print(f"   TP: {signal.take_profit}")
        
        # Parse raw signal data
        if signal.raw_signal_data:
            import json
            raw_data = json.loads(signal.raw_signal_data)
            print(f"   BOS Level: {raw_data.get('h1_bos_level')}")
            print(f"   BOS Direction: {raw_data.get('h1_bos_direction')}")
            print(f"   M15 Break High: {raw_data.get('m15_break_high')}")
            print(f"   Pip Trigger: {raw_data.get('pip_trigger')}")
            
    except Exception as e:
        print(f"   ERROR: {e}")

if __name__ == "__main__":
    signal_id = test_pure_ea_webhook()
    check_signal_in_database(signal_id)
    
    print("\n=== TEST COMPLETED ===")
    if signal_id:
        print("SUCCESS: PURE EA webhook working! Signal stored and ready for AI analysis.")
    else:
        print("FAILED: PURE EA webhook not working correctly.")