"""
Test Discord webhook with sample trading signals
"""
import requests
import json

def test_discord_webhook():
    """Test Discord webhook with various signal formats"""
    
    webhook_url = "http://127.0.0.1:8000/signals/discord-webhook/"
    
    # Test signals in different formats
    test_signals = [
        # Format 1: Standard format
        "EURUSD BUY Entry: 1.0850 SL: 1.0800 TP: 1.0900",
        
        # Format 2: Compact format  
        "GBPUSD SELL 1.2750 SL:1.2800 TP:1.2650",
        
        # Format 3: Verbose format
        "Symbol: AUDUSD Direction: BUY Entry: 0.6250 Stop: 0.6200 Target: 0.6350",
        
        # Format 4: Real Discord message style
        """NEW SIGNAL ALERT
        
        USDJPY BUY
        Entry: 149.50
        SL: 149.00  
        TP: 150.50
        
        Good luck traders!""",
    ]
    
    print("Testing Discord webhook...")
    
    for i, signal in enumerate(test_signals, 1):
        print(f"\n--- Test {i} ---")
        print(f"Signal: {signal.strip()[:50]}...")
        
        try:
            response = requests.post(
                webhook_url,
                json={'content': signal},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS: {result}")
            else:
                print(f"❌ FAILED: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n🎉 Test completed! Check your dashboard for new signals.")

if __name__ == "__main__":
    test_discord_webhook()