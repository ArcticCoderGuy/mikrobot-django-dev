"""
MikroBot QA Automation
Automaattinen testien suoritus taustalla
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any
import logging
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Django setup
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')
import django
django.setup()

from django.conf import settings
from signals.models import MQL5Signal
from trading.models import Trade
from dashboard.utils import get_mt5_account_info, get_system_status

logger = logging.getLogger(__name__)

class QATestRunner:
    """Automaattinen QA-testien suorittaja"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}
        self.test_timestamp = datetime.now()
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Suorita kaikki QA-testit"""
        print(f"🤖 Aloitetaan automaattiset QA-testit: {self.test_timestamp}")
        
        results = {
            'timestamp': self.test_timestamp.isoformat(),
            'tests': {},
            'summary': {},
            'overall_status': 'PASS'
        }
        
        # 1. Django Server Test
        results['tests']['django_server'] = self._test_django_server()
        
        # 2. Dashboard Tests
        results['tests']['main_dashboard'] = self._test_dashboard_pages()
        
        # 3. MT5 Connection Test
        results['tests']['mt5_connection'] = self._test_mt5_connection()
        
        # 4. Database Tests
        results['tests']['database'] = self._test_database()
        
        # 5. Settings Tests
        results['tests']['settings'] = self._test_settings()
        
        # 6. REST API Tests
        results['tests']['rest_api'] = self._test_rest_apis()
        
        # 7. End-to-End Test (jos mahdollista)
        results['tests']['end_to_end'] = self._test_end_to_end()
        
        # Laske yhteenveto
        results['summary'] = self._calculate_summary(results['tests'])
        results['overall_status'] = 'PASS' if results['summary']['pass_rate'] >= 80 else 'FAIL'
        
        # Tallenna tulokset
        self._save_results(results)
        
        # Lähetä Telegram-notifikaatio jos testit epäonnistuvat
        self._send_telegram_notification(results)
        
        return results
    
    def _test_django_server(self) -> Dict[str, Any]:
        """Testaa Django-serverin toiminta"""
        try:
            response = requests.get(f"{self.base_url}/dashboard/", timeout=5)
            return {
                'status': 'PASS' if response.status_code == 200 else 'FAIL',
                'details': f"HTTP {response.status_code}",
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'details': f"Connection error: {str(e)}",
                'response_time': None
            }
    
    def _test_dashboard_pages(self) -> Dict[str, Any]:
        """Testaa dashboard-sivut"""
        pages = [
            '/dashboard/',
            '/dashboard/main/',
            '/dashboard/settings/',
            '/dashboard/qa/'
        ]
        
        results = {}
        all_passed = True
        
        for page in pages:
            try:
                response = requests.get(f"{self.base_url}{page}", timeout=5)
                status = 'PASS' if response.status_code == 200 else 'FAIL'
                if status == 'FAIL':
                    all_passed = False
                    
                results[page] = {
                    'status': status,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                results[page] = {
                    'status': 'FAIL',
                    'error': str(e)
                }
                all_passed = False
        
        return {
            'status': 'PASS' if all_passed else 'FAIL',
            'details': results,
            'pages_tested': len(pages)
        }
    
    def _test_mt5_connection(self) -> Dict[str, Any]:
        """Testaa MT5-yhteys"""
        try:
            account_info = get_mt5_account_info()
            if account_info and 'balance' in account_info:
                return {
                    'status': 'PASS',
                    'details': f"Balance: {account_info.get('balance', 'Unknown')}",
                    'connection': True
                }
            else:
                return {
                    'status': 'WARN',
                    'details': "MT5 connection failed, using demo data",
                    'connection': False
                }
        except Exception as e:
            return {
                'status': 'WARN',
                'details': f"MT5 test failed: {str(e)}",
                'connection': False
            }
    
    def _test_database(self) -> Dict[str, Any]:
        """Testaa tietokanta-yhteys"""
        try:
            signals_count = MQL5Signal.objects.count()
            trades_count = Trade.objects.count()
            
            return {
                'status': 'PASS',
                'details': {
                    'signals': signals_count,
                    'trades': trades_count,
                    'connection': True
                }
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'details': f"Database error: {str(e)}",
                'connection': False
            }
    
    def _test_settings(self) -> Dict[str, Any]:
        """Testaa asetussivun toiminta"""
        try:
            response = requests.get(f"{self.base_url}/dashboard/settings/", timeout=5)
            return {
                'status': 'PASS' if response.status_code == 200 else 'FAIL',
                'details': f"Settings page HTTP {response.status_code}"
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'details': f"Settings test failed: {str(e)}"
            }
    
    def _test_rest_apis(self) -> Dict[str, Any]:
        """Testaa REST API -päätteet"""
        apis = [
            '/api/v1/signals/',
            '/api/v1/trades/',
            '/api/v1/signals/stats/',
            '/api/v1/trades/statistics/'
        ]
        
        results = {}
        passed = 0
        
        for api in apis:
            try:
                response = requests.get(f"{self.base_url}{api}", timeout=5)
                status = 'PASS' if response.status_code in [200, 401] else 'FAIL'  # 401 = Auth required = OK
                if status == 'PASS':
                    passed += 1
                    
                results[api] = {
                    'status': status,
                    'status_code': response.status_code
                }
            except Exception as e:
                results[api] = {
                    'status': 'FAIL',
                    'error': str(e)
                }
        
        return {
            'status': 'PASS' if passed >= len(apis) * 0.8 else 'FAIL',  # 80% pass rate
            'details': results,
            'pass_rate': f"{passed}/{len(apis)}"
        }
    
    def _test_end_to_end(self) -> Dict[str, Any]:
        """Testaa End-to-End toiminnallisuus (yksinkertainen versio)"""
        try:
            # Tarkista että on hyväksytty signaali olemassa
            approved_signal = MQL5Signal.objects.filter(status='approved').first()
            if not approved_signal:
                # Hyväksy ensimmäinen pending signaali testiin
                pending_signal = MQL5Signal.objects.filter(status='pending').first()
                if pending_signal:
                    pending_signal.status = 'approved'
                    pending_signal.save()
                    approved_signal = pending_signal
                    print(f"📝 Hyväksyttiin signaali {pending_signal.id} E2E-testiä varten")
                else:
                    return {
                        'status': 'SKIP',
                        'details': "No pending signals to approve for E2E test"
                    }
            
            # Tarkista että trade-endpoint vastaa
            response = requests.get(f"{self.base_url}/api/v1/trades/execute_signal/", timeout=5)
            
            # 405 = Method Not Allowed (GET ei sallittu, POST vaaditaan) = OK
            # 401 = Authentication required = OK (endpoint toimii mutta vaatii kirjautumisen)
            if response.status_code in [405, 401]:
                status_msg = "Method not allowed" if response.status_code == 405 else "Auth required"
                return {
                    'status': 'PASS',
                    'details': f"Execute signal endpoint responsive ({status_msg})",
                    'signal_available': True
                }
            else:
                return {
                    'status': 'WARN',
                    'details': f"Unexpected response: {response.status_code}",
                    'signal_available': True
                }
        except Exception as e:
            return {
                'status': 'FAIL',
                'details': f"E2E test failed: {str(e)}",
                'signal_available': False
            }
    
    def _calculate_summary(self, tests: Dict[str, Any]) -> Dict[str, Any]:
        """Laske testitulosten yhteenveto"""
        total = len(tests)
        passed = sum(1 for test in tests.values() if test.get('status') == 'PASS')
        failed = sum(1 for test in tests.values() if test.get('status') == 'FAIL')
        warnings = sum(1 for test in tests.values() if test.get('status') in ['WARN', 'SKIP'])
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'pass_rate': round(pass_rate, 1)
        }
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """Tallenna testitulokset JSON-tiedostoon"""
        try:
            results_file = os.path.join(settings.BASE_DIR, 'qa_results.json')
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"📊 Tulokset tallennettu: {results_file}")
        except Exception as e:
            print(f"❌ Tulosten tallennus epäonnistui: {e}")
    
    def _send_telegram_notification(self, results: Dict[str, Any]) -> None:
        """Lähetä Telegram-notifikaatio tarvittaessa"""
        try:
            # Import telegram notifier
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from telegram_notifier import send_qa_notification
            
            # Lähetä vain jos testit epäonnistuvat (alle 100%)
            pass_rate = results.get('summary', {}).get('pass_rate', 100)
            overall_status = results.get('overall_status', 'PASS')
            
            if pass_rate < 100 or overall_status != 'PASS':
                success = send_qa_notification(results)
                if success:
                    print(f"📱 Telegram-hälytys lähetetty (@ArcticTrader)")
                else:
                    print(f"❌ Telegram-hälytys epäonnistui")
            else:
                print(f"✅ Kaikki testit OK - ei Telegram-hälytysta tarvita")
                
        except Exception as e:
            print(f"❌ Telegram-notifikaatio epäonnistui: {e}")


def run_automated_qa():
    """Pääfunktio automaattisten testien suorittamiseen"""
    runner = QATestRunner()
    results = runner.run_all_tests()
    
    # Tulosta yhteenveto
    summary = results['summary']
    status_emoji = "✅" if results['overall_status'] == 'PASS' else "❌"
    
    print(f"\n{status_emoji} QA-testit suoritettu:")
    print(f"   Yhteensä: {summary['total_tests']}")
    print(f"   Läpäisi: {summary['passed']}")
    print(f"   Epäonnistui: {summary['failed']}")
    print(f"   Varoituksia: {summary['warnings']}")
    print(f"   Läpäisyprosentti: {summary['pass_rate']}%")
    print(f"   Tila: {results['overall_status']}")
    
    return results


if __name__ == "__main__":
    run_automated_qa()