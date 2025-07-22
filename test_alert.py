"""Test Telegram Alert"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from dashboard.telegram_notifier import TelegramNotifier

# Luo demo QA-tulokset
qa_results = {
    'timestamp': '2025-07-21T17:50:00',
    'overall_status': 'FAIL',
    'summary': {
        'total_tests': 7,
        'passed': 5,
        'failed': 2,
        'warnings': 0,
        'pass_rate': 71.4
    },
    'tests': {
        'django_server': {'status': 'FAIL', 'details': 'Connection refused'},
        'mt5_connection': {'status': 'FAIL', 'details': 'MT5 not running'}
    }
}

print("📱 Lähetetään testi-hälytys...")
notifier = TelegramNotifier()
success = notifier.send_qa_alert(qa_results)

if success:
    print("✅ Hälytys lähetetty onnistuneesti @ArcticTrader:lle!")
else:
    print("❌ Hälytyksen lähetys epäonnistui")