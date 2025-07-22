"""
Telegram Notification System
Lähettää QA-virheet ja järjestelmäilmoitukset Telegramiin
"""

import requests
import json
import logging
import sys
import io
from datetime import datetime
from typing import Dict, Any, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    Telegram-viestien lähetys
    Käyttää Telegram Bot API:a
    """
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        # MikroBot Telegram Bot (luo bot @BotFather:ssa)
        self.bot_token = bot_token or "8139279606:AAFay9O4LDPQTRQQ6jjaDWeQxqeOmfoapi0"  # MikroBot QA Monitor
        # ArcticTrader's chat ID
        self.chat_id = chat_id or "260783230"  # @ArcticTrader
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Lähetä viesti Telegramiin"""
        
        # DEMO MODE - Näytä viesti konsolissa ilman oikeaa bot tokenia
        if self.bot_token == "YOUR_BOT_TOKEN_HERE":
            print(f"\n📱 DEMO TELEGRAM MESSAGE to {self.chat_id}:")
            print("=" * 50)
            print(message)
            print("=" * 50)
            print(f"✅ Demo-viesti näytetty onnistuneesti!")
            return True
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"📱 Telegram-viesti lähetetty onnistuneesti: {self.chat_id}")
                return True
            else:
                print(f"❌ Telegram-viestin lähetys epäonnistui: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram-virhe: {e}")
            return False
    
    def send_qa_alert(self, qa_results: Dict[str, Any]) -> bool:
        """Lähetä QA-hälytys jos testit epäonnistuvat"""
        
        summary = qa_results.get('summary', {})
        overall_status = qa_results.get('overall_status', 'UNKNOWN')
        timestamp = qa_results.get('timestamp', datetime.now().isoformat())
        
        # Älä lähetä ilmoitusta jos kaikki OK
        if overall_status == 'PASS' and summary.get('pass_rate', 0) >= 100:
            return True  # Ei lähetystä tarvita
        
        # Muodosta hälytysviesti
        pass_rate = summary.get('pass_rate', 0)
        passed = summary.get('passed', 0)
        total = summary.get('total_tests', 0)
        failed = summary.get('failed', 0)
        warnings = summary.get('warnings', 0)
        
        # Määritä vakavuus
        if pass_rate < 50:
            alert_level = "🚨 CRITICAL"
            emoji = "🚨"
        elif pass_rate < 80:
            alert_level = "⚠️ WARNING"  
            emoji = "⚠️"
        else:
            alert_level = "🔍 NOTICE"
            emoji = "🔍"
        
        message = f"""
{emoji} **MikroBot QA Alert**

{alert_level}: QA Tests below 100%

📊 **Results:**
• Pass Rate: {pass_rate}%
• Tests: {passed}/{total}
• Failed: {failed}
• Warnings: {warnings}

🕒 **Time:** {datetime.fromisoformat(timestamp).strftime('%H:%M:%S')}

🔍 **Failed Tests:**
"""
        
        # Lisää epäonnistuneiden testien yksityiskohdat
        tests = qa_results.get('tests', {})
        failed_details = []
        
        for test_name, test_result in tests.items():
            status = test_result.get('status', 'UNKNOWN')
            if status in ['FAIL', 'WARN', 'ERROR']:
                details = test_result.get('details', 'No details')
                failed_details.append(f"• {test_name}: {status} - {details}")
        
        if failed_details:
            message += "\n".join(failed_details)
        else:
            message += "• No specific failures detected"
        
        message += f"\n\n🖥️ **Dashboard:** http://localhost:8000/dashboard/"
        
        return self.send_message(message)
    
    def send_system_alert(self, title: str, message: str, level: str = "INFO") -> bool:
        """Lähetä yleinen järjestelmäilmoitus"""
        
        level_emojis = {
            "INFO": "ℹ️",
            "WARN": "⚠️", 
            "ERROR": "❌",
            "CRITICAL": "🚨",
            "SUCCESS": "✅"
        }
        
        emoji = level_emojis.get(level, "ℹ️")
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        telegram_message = f"""
{emoji} **MikroBot System Alert**

**{title}**

{message}

🕒 **Time:** {timestamp}
"""
        
        return self.send_message(telegram_message)
    
    def test_connection(self) -> bool:
        """Testaa Telegram-yhteys"""
        test_message = f"""
🤖 **MikroBot Telegram Test**

Telegram-notifikaatiot käytössä!

🕒 **Time:** {datetime.now().strftime('%H:%M:%S')}
📊 **Status:** Connection OK
"""
        
        return self.send_message(test_message)


def send_qa_notification(qa_results: Dict[str, Any]) -> bool:
    """Pääfunktio QA-notifikaatioiden lähettämiseen"""
    
    try:
        notifier = TelegramNotifier()
        return notifier.send_qa_alert(qa_results)
    except Exception as e:
        print(f"❌ QA notification failed: {e}")
        return False


if __name__ == "__main__":
    # Testaa Telegram-yhteys
    notifier = TelegramNotifier()
    
    print("📱 Testing Telegram connection...")
    success = notifier.test_connection()
    
    if success:
        print("✅ Telegram notification system is working!")
    else:
        print("❌ Telegram notification system failed!")
        print("1. Create a bot via @BotFather")
        print("2. Get your bot token") 
        print("3. Start a chat with your bot")
        print("4. Update bot_token in telegram_notifier.py")