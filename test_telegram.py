"""
Simple Telegram Test
Näyttää miltä Telegram-viestit näyttäisivät
"""

import sys
import io
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def show_test_messages():
    print("🤖 MikroBot Telegram Notification Demo")
    print("=" * 60)
    
    # 1. Yhteyden testaus
    print("\n📱 1. CONNECTION TEST MESSAGE:")
    print("-" * 40)
    test_message = """
🤖 **MikroBot Telegram Test**

Telegram-notifikaatiot käytössä!

🕒 **Time:** 15:30:00
📊 **Status:** Connection OK
"""
    print(test_message)
    
    # 2. QA Alert - Warning
    print("\n📱 2. QA WARNING ALERT:")
    print("-" * 40)
    warning_message = """
⚠️ **MikroBot QA Alert**

⚠️ WARNING: QA Tests below 100%

📊 **Results:**
• Pass Rate: 85.7%
• Tests: 6/7
• Failed: 0
• Warnings: 1

🕒 **Time:** 15:30:25

🔍 **Failed Tests:**
• end_to_end: WARN - Authentication required

🖥️ **Dashboard:** http://localhost:8000/dashboard/
"""
    print(warning_message)
    
    # 3. QA Alert - Critical
    print("\n📱 3. QA CRITICAL ALERT:")
    print("-" * 40)
    critical_message = """
🚨 **MikroBot QA Alert**

🚨 CRITICAL: QA Tests below 100%

📊 **Results:**
• Pass Rate: 42.9%
• Tests: 3/7
• Failed: 3
• Warnings: 1

🕒 **Time:** 15:31:15

🔍 **Failed Tests:**
• django_server: FAIL - Connection refused
• mt5_connection: FAIL - MT5 not running
• database: FAIL - Connection timeout
• end_to_end: WARN - No signals available

🖥️ **Dashboard:** http://localhost:8000/dashboard/
"""
    print(critical_message)
    
    # 4. System Alert
    print("\n📱 4. SYSTEM ALERT:")
    print("-" * 40)
    system_message = """
✅ **MikroBot System Alert**

**QA System Started**

Automatic QA monitoring is now active.
Tests will run every 15 minutes.

You will receive alerts only when:
• Pass rate drops below 100%
• System components fail
• Critical errors occur

🕒 **Time:** 15:32:00
"""
    print(system_message)
    
    print("\n" + "=" * 60)
    print("📱 Demo complete! These messages will be sent to @ArcticTrader")
    print("💡 To enable: Create Telegram bot and add token to telegram_notifier.py")

if __name__ == "__main__":
    show_test_messages()