import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

# Fix Unicode issues on Windows
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# Get credentials
login = int(os.getenv('MT5_LOGIN', '0'))
password = os.getenv('MT5_PASSWORD', '')
server = os.getenv('MT5_SERVER', '')

print(f"Testing MT5 connection...")
print(f"Login: {login}")
print(f"Server: {server}")
print(f"Password: {'*' * len(password)}")

# Initialize MT5
if mt5.initialize():
    print("\n✅ MT5 initialized successfully!")
    
    # Try to login
    if mt5.login(login, password, server):
        print("✅ Login successful!")
        
        # Get account info
        account_info = mt5.account_info()
        if account_info:
            print(f"\n📊 Account Info:")
            print(f"Balance: ${account_info.balance}")
            print(f"Equity: ${account_info.equity}")
            print(f"Leverage: 1:{account_info.leverage}")
            print(f"Server: {account_info.server}")
            
        # Check EURUSD symbol
        symbol_info = mt5.symbol_info("EURUSD")
        if symbol_info:
            print(f"\n💱 EURUSD Info:")
            print(f"Bid: {symbol_info.bid}")
            print(f"Ask: {symbol_info.ask}")
            print(f"Spread: {(symbol_info.ask - symbol_info.bid) * 10000:.1f} pips")
        else:
            print("\n⚠️ EURUSD not found!")
    else:
        error = mt5.last_error()
        print(f"❌ Login failed! Error: {error}")
        
    mt5.shutdown()
else:
    print("❌ MT5 initialization failed!")
    print(f"Error: {mt5.last_error()}")