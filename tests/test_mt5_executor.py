"""
MikroBot MT5Executor Yksikkötestit
Testaa MetaTrader 5 integraation toimivuuden
Käyttää mock-objekteja, joten ei vaadi oikeaa MT5-yhteyttä
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import os
from decimal import Decimal
from datetime import datetime, timezone
import uuid

# Aseta Django settings ennen importteja
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')

import django
django.setup()

from trading.mt5_executor import (
    MT5Executor, 
    MT5ExecutionResult, 
    MT5ConnectionConfig,
    execute_approved_signal,
    close_trade_by_ticket,
    update_trade_from_mt5
)
from signals.models import MQL5Signal
from trading.models import Trade


class TestMT5Executor(unittest.TestCase):
    """MT5Executor luokan testit"""
    
    def setUp(self):
        """Alusta testit"""
        self.valid_config = MT5ConnectionConfig(
            login=123456,
            password="test_password",
            server="TestBroker-Demo"
        )
        
        # Luo mock signaali testausta varten
        self.test_signal = MagicMock(spec=MQL5Signal)
        self.test_signal.id = uuid.uuid4()
        self.test_signal.status = 'approved'
        self.test_signal.symbol = 'EURUSD'
        self.test_signal.direction = 'BUY'
        self.test_signal.entry_price = Decimal('1.0850')
        self.test_signal.stop_loss = Decimal('1.0800')
        self.test_signal.take_profit = Decimal('1.0900')
        
    def test_default_config_from_settings(self):
        """Testaa että oletuskonfiguraatio ladataan settings.py:stä"""
        with patch('trading.mt5_executor.settings') as mock_settings:
            mock_settings.MT5_CONFIG = {
                'login': 999999,
                'password': 'settings_password',
                'server': 'SettingsBroker',
                'timeout': 5000,
                'portable': True
            }
            
            executor = MT5Executor()
            self.assertEqual(executor.config.login, 999999)
            self.assertEqual(executor.config.password, 'settings_password')
            self.assertEqual(executor.config.server, 'SettingsBroker')
            self.assertEqual(executor.config.timeout, 5000)
            self.assertTrue(executor.config.portable)
    
    @patch('trading.mt5_executor.mt5')
    def test_successful_connection(self, mock_mt5):
        """Testaa onnistunut MT5-yhteys"""
        # Mock account info
        mock_account = MagicMock()
        mock_account.login = 123456
        
        mock_mt5.initialize.return_value = True
        mock_mt5.account_info.return_value = mock_account
        
        executor = MT5Executor(self.valid_config)
        result = executor.connect()
        
        self.assertTrue(result)
        self.assertTrue(executor.connected)
        mock_mt5.initialize.assert_called_once()
        
    @patch('trading.mt5_executor.mt5')
    def test_failed_connection(self, mock_mt5):
        """Testaa epäonnistunut MT5-yhteys"""
        mock_mt5.initialize.return_value = False
        mock_mt5.last_error.return_value = (1, "Connection failed")
        
        executor = MT5Executor(self.valid_config)
        result = executor.connect()
        
        self.assertFalse(result)
        self.assertFalse(executor.connected)
        
    @patch('trading.mt5_executor.mt5')
    def test_execute_trade_from_signal_buy(self, mock_mt5):
        """Testaa BUY-kaupan suoritus signaalista"""
        # Setup mocks
        mock_mt5.initialize.return_value = True
        mock_mt5.account_info.return_value = MagicMock(login=123456)
        
        mock_symbol_info = MagicMock()
        mock_symbol_info.visible = True
        mock_symbol_info.volume_min = 0.01
        mock_symbol_info.volume_max = 100.0
        mock_symbol_info.volume_step = 0.01
        mock_symbol_info.point = 0.00001
        mock_mt5.symbol_info.return_value = mock_symbol_info
        
        mock_tick = MagicMock()
        mock_tick.ask = 1.0855
        mock_tick.bid = 1.0853
        mock_mt5.symbol_info_tick.return_value = mock_tick
        
        # Mock successful order
        mock_result = MagicMock()
        mock_result.retcode = 10009  # TRADE_RETCODE_DONE
        mock_result.order = 12345678
        mock_result.price = 1.0855
        mock_result.volume = 0.01
        mock_result.comment = "Request executed"
        mock_mt5.order_send.return_value = mock_result
        mock_mt5.TRADE_RETCODE_DONE = 10009
        mock_mt5.ORDER_TYPE_BUY = 0
        
        executor = MT5Executor(self.valid_config)
        result = executor.execute_trade_from_signal(self.test_signal, Decimal('0.01'))
        
        self.assertTrue(result.success)
        self.assertEqual(result.ticket, 12345678)
        self.assertEqual(result.actual_entry_price, Decimal('1.0855'))
        self.assertEqual(result.actual_volume, Decimal('0.01'))
        
    @patch('trading.mt5_executor.mt5')
    def test_execute_trade_from_signal_sell(self, mock_mt5):
        """Testaa SELL-kaupan suoritus signaalista"""
        # Muuta signaali SELL-suuntaan
        self.test_signal.direction = 'SELL'
        
        # Setup mocks
        mock_mt5.initialize.return_value = True
        mock_mt5.account_info.return_value = MagicMock(login=123456)
        
        mock_symbol_info = MagicMock()
        mock_symbol_info.visible = True
        mock_symbol_info.volume_min = 0.01
        mock_symbol_info.volume_max = 100.0
        mock_symbol_info.volume_step = 0.01
        mock_symbol_info.point = 0.00001
        mock_mt5.symbol_info.return_value = mock_symbol_info
        
        mock_tick = MagicMock()
        mock_tick.ask = 1.0855
        mock_tick.bid = 1.0853
        mock_mt5.symbol_info_tick.return_value = mock_tick
        
        # Mock successful order
        mock_result = MagicMock()
        mock_result.retcode = 10009
        mock_result.order = 87654321
        mock_result.price = 1.0853
        mock_result.volume = 0.01
        mock_mt5.order_send.return_value = mock_result
        mock_mt5.TRADE_RETCODE_DONE = 10009
        mock_mt5.ORDER_TYPE_SELL = 1
        
        executor = MT5Executor(self.valid_config)
        result = executor.execute_trade_from_signal(self.test_signal, Decimal('0.01'))
        
        self.assertTrue(result.success)
        self.assertEqual(result.ticket, 87654321)
        self.assertEqual(result.actual_entry_price, Decimal('1.0853'))
        
    @patch('trading.mt5_executor.mt5')
    def test_execute_trade_unapproved_signal(self, mock_mt5):
        """Testaa että hyväksymätön signaali ei suorita kauppaa"""
        self.test_signal.status = 'pending'
        
        executor = MT5Executor(self.valid_config)
        result = executor.execute_trade_from_signal(self.test_signal, Decimal('0.01'))
        
        self.assertFalse(result.success)
        self.assertIn('not approved', result.error_message)
        
    @patch('trading.mt5_executor.mt5')
    def test_close_trade(self, mock_mt5):
        """Testaa kaupan sulkeminen"""
        # Setup mocks
        mock_mt5.initialize.return_value = True
        mock_mt5.account_info.return_value = MagicMock(login=123456)
        
        # Mock open position
        mock_position = MagicMock()
        mock_position.ticket = 12345678
        mock_position.symbol = 'EURUSD'
        mock_position.type = 0  # POSITION_TYPE_BUY
        mock_position.volume = 0.01
        mock_mt5.positions_get.return_value = [mock_position]
        mock_mt5.POSITION_TYPE_BUY = 0
        
        # Mock tick for close price
        mock_tick = MagicMock()
        mock_tick.bid = 1.0860
        mock_tick.ask = 1.0862
        mock_mt5.symbol_info_tick.return_value = mock_tick
        
        # Mock successful close
        mock_result = MagicMock()
        mock_result.retcode = 10009
        mock_result.order = 99999999
        mock_result.price = 1.0860
        mock_mt5.order_send.return_value = mock_result
        mock_mt5.TRADE_RETCODE_DONE = 10009
        mock_mt5.ORDER_TYPE_SELL = 1
        
        executor = MT5Executor(self.valid_config)
        result = executor.close_trade(12345678)
        
        self.assertTrue(result.success)
        self.assertEqual(result.ticket, 99999999)
        self.assertEqual(result.actual_entry_price, Decimal('1.0860'))
        
    @patch('trading.mt5_executor.mt5')
    def test_get_position_info(self, mock_mt5):
        """Testaa position tietojen haku"""
        # Setup mocks
        mock_mt5.initialize.return_value = True
        mock_mt5.account_info.return_value = MagicMock(login=123456)
        
        # Mock position data
        mock_position = MagicMock()
        mock_position.ticket = 12345678
        mock_position.symbol = 'EURUSD'
        mock_position.type = 0  # BUY
        mock_position.volume = 0.01
        mock_position.price_open = 1.0850
        mock_position.price_current = 1.0855
        mock_position.sl = 1.0800
        mock_position.tp = 1.0900
        mock_position.profit = 5.00
        mock_position.swap = -0.50
        mock_position.commission = -2.00
        mock_position.time = 1642598400  # Unix timestamp
        
        mock_mt5.positions_get.return_value = [mock_position]
        mock_mt5.POSITION_TYPE_BUY = 0
        
        executor = MT5Executor(self.valid_config)
        info = executor.get_position_info(12345678)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['ticket'], 12345678)
        self.assertEqual(info['symbol'], 'EURUSD')
        self.assertEqual(info['type'], 'BUY')
        self.assertEqual(info['volume'], 0.01)
        self.assertEqual(info['profit'], 5.00)
        
    @patch('trading.mt5_executor.mt5')
    def test_get_account_info(self, mock_mt5):
        """Testaa tilin tietojen haku"""
        # Setup mocks
        mock_mt5.initialize.return_value = True
        
        # Mock account data
        mock_account = MagicMock()
        mock_account.login = 123456
        mock_account.server = 'TestBroker-Demo'
        mock_account.currency = 'USD'
        mock_account.company = 'Test Broker Ltd'
        mock_account.balance = 10000.00
        mock_account.equity = 10050.00
        mock_account.margin = 100.00
        mock_account.margin_free = 9950.00
        mock_account.margin_level = 10050.00
        mock_account.profit = 50.00
        
        mock_mt5.account_info.return_value = mock_account
        
        executor = MT5Executor(self.valid_config)
        info = executor.get_account_info()
        
        self.assertIsNotNone(info)
        self.assertEqual(info['login'], 123456)
        self.assertEqual(info['balance'], 10000.00)
        self.assertEqual(info['equity'], 10050.00)
        self.assertEqual(info['profit'], 50.00)
        
    @patch('trading.mt5_executor.mt5')
    def test_normalize_volume(self, mock_mt5):
        """Testaa volyymin normalisointi"""
        # Setup symbol info
        mock_symbol_info = MagicMock()
        mock_symbol_info.volume_min = 0.01
        mock_symbol_info.volume_max = 100.0
        mock_symbol_info.volume_step = 0.01
        mock_mt5.symbol_info.return_value = mock_symbol_info
        
        executor = MT5Executor(self.valid_config)
        
        # Testi: liian pieni volyymi
        normalized = executor._normalize_volume('EURUSD', 0.001)
        self.assertEqual(normalized, 0.01)
        
        # Testi: liian suuri volyymi
        normalized = executor._normalize_volume('EURUSD', 1000.0)
        self.assertEqual(normalized, 100.0)
        
        # Testi: pyöristys volume_step mukaan
        normalized = executor._normalize_volume('EURUSD', 0.123)
        self.assertEqual(normalized, 0.12)
        
    @patch('trading.mt5_executor.mt5')
    def test_context_manager(self, mock_mt5):
        """Testaa context manager toiminta"""
        mock_mt5.initialize.return_value = True
        mock_mt5.account_info.return_value = MagicMock(login=123456)
        
        with MT5Executor(self.valid_config) as executor:
            self.assertTrue(executor.connected)
            
        # Yhteyden pitäisi olla suljettu contextin jälkeen
        mock_mt5.shutdown.assert_called_once()
        

class TestMT5HelperFunctions(unittest.TestCase):
    """Testit helper-funktioille"""
    
    @patch('trading.mt5_executor.MQL5Signal.objects.get')
    @patch('trading.mt5_executor.MT5Executor')
    def test_execute_approved_signal_success(self, mock_executor_class, mock_signal_get):
        """Testaa execute_approved_signal onnistunut suoritus"""
        # Mock signal
        mock_signal = MagicMock(spec=MQL5Signal)
        mock_signal.status = 'approved'
        mock_signal_get.return_value = mock_signal
        
        # Mock executor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Mock successful execution
        mock_result = MT5ExecutionResult(
            success=True,
            ticket=12345678,
            actual_entry_price=Decimal('1.0855'),
            actual_volume=Decimal('0.01')
        )
        mock_executor.execute_trade_from_signal.return_value = mock_result
        
        # Execute
        success, message, ticket = execute_approved_signal('test-signal-id', Decimal('0.01'))
        
        self.assertTrue(success)
        self.assertIn('successfully', message)
        self.assertEqual(ticket, 12345678)
        
        # Varmista että signaali merkittiin suoritetuksi
        self.assertEqual(mock_signal.status, 'executed')
        mock_signal.save.assert_called_once()
        
    @patch('trading.mt5_executor.MT5Executor')
    def test_close_trade_by_ticket_success(self, mock_executor_class):
        """Testaa close_trade_by_ticket onnistunut suoritus"""
        # Mock executor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Mock successful close
        mock_result = MT5ExecutionResult(
            success=True,
            ticket=99999999
        )
        mock_executor.close_trade.return_value = mock_result
        
        # Execute
        success, message = close_trade_by_ticket(12345678)
        
        self.assertTrue(success)
        self.assertIn('successfully', message)
        

if __name__ == '__main__':
    unittest.main()