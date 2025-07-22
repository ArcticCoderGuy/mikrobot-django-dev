"""
Debug Simple Trading Solutions parser
"""
import re
from decimal import Decimal

def debug_parse_signal(message):
    print("=== DEBUG PARSER ===")
    message = message.upper().strip()
    print(f"Upper message:\n{message}")
    
    print(f"\n1. Looking for 'RECOMMENDED ACTION: BUY': {'RECOMMENDED ACTION: BUY' in message}")
    print(f"2. Looking for 'RECOMMENDED ACTION: SELL': {'RECOMMENDED ACTION: SELL' in message}")
    
    if 'RECOMMENDED ACTION: BUY' in message:
        print("\n=== Parsing BUY signal ===")
        symbol_match = re.search(r'TRADE READY ON ([A-Z]{6})', message)
        entry_match = re.search(r'BUY TRADE PARAMETERS:.*?ENTRY: ([\d.]+)', message, re.DOTALL)
        sl_match = re.search(r'BUY TRADE PARAMETERS:.*?SL:.*?- ([\d.]+)', message, re.DOTALL)
        tp_match = re.search(r'BUY TRADE PARAMETERS:.*?TP1:.*?- ([\d.]+)', message, re.DOTALL)
        
        print(f"Symbol match: {symbol_match.group(1) if symbol_match else None}")
        print(f"Entry match: {entry_match.group(1) if entry_match else None}")
        print(f"SL match: {sl_match.group(1) if sl_match else None}")
        print(f"TP match: {tp_match.group(1) if tp_match else None}")
        
        if symbol_match and entry_match and sl_match and tp_match:
            return {
                'symbol': symbol_match.group(1),
                'direction': 'BUY',
                'entry': Decimal(entry_match.group(1)),
                'sl': Decimal(sl_match.group(1)),
                'tp': Decimal(tp_match.group(1))
            }
    
    print("\nNo match found!")
    return None

# Test with Simple Trading Solutions signal
signal = """Trade READY on AUDUSD!
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

result = debug_parse_signal(signal)
print(f"\nResult: {result}")