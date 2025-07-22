import MetaTrader5 as mt5
import logging
import time
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone as django_timezone

from .models import Trade
from signals.models import MQL5Signal

logger = logging.getLogger(__name__)


@dataclass
class MT5ExecutionResult:
    """Result of MT5 trade execution"""
    success: bool
    ticket: Optional[int] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    actual_entry_price: Optional[Decimal] = None
    actual_volume: Optional[Decimal] = None
    execution_time: Optional[datetime] = None


@dataclass
class MT5ConnectionConfig:
    """MT5 connection configuration"""
    login: int
    password: str
    server: str
    timeout: int = 10000
    portable: bool = False


class MT5Executor:
    """
    MetaTrader 5 trade execution and management
    """
    
    def __init__(self, config: Optional[MT5ConnectionConfig] = None):
        self.config = config or self._get_default_config()
        self.connected = False
        self.deviation = 20  # Price deviation in points
        self.magic_number = 20250117  # Unique magic number for MikroBot
        
    def _get_default_config(self) -> MT5ConnectionConfig:
        """Get default MT5 configuration from settings"""
        mt5_config = getattr(settings, 'MT5_CONFIG', {})
        return MT5ConnectionConfig(
            login=mt5_config.get('login', 0),
            password=mt5_config.get('password', ''),
            server=mt5_config.get('server', ''),
            timeout=mt5_config.get('timeout', 10000),
            portable=mt5_config.get('portable', False)
        )
    
    def connect(self) -> bool:
        """Connect to MetaTrader 5"""
        try:
            # Initialize MT5 connection
            if not mt5.initialize(
                login=self.config.login,
                password=self.config.password,
                server=self.config.server,
                timeout=self.config.timeout,
                portable=self.config.portable
            ):
                error_code = mt5.last_error()
                logger.error(f"MT5 initialization failed: {error_code}")
                return False
            
            # Check connection
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                mt5.shutdown()
                return False
            
            self.connected = True
            logger.info(f"MT5 connected successfully. Account: {account_info.login}")
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MetaTrader 5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("MT5 disconnected")
    
    def execute_trade_from_signal(self, signal: MQL5Signal, volume: Decimal) -> MT5ExecutionResult:
        """Execute trade based on approved signal"""
        if not self.connected:
            if not self.connect():
                return MT5ExecutionResult(
                    success=False,
                    error_message="Failed to connect to MT5"
                )
        
        try:
            # Validate signal
            if signal.status != 'approved':
                return MT5ExecutionResult(
                    success=False,
                    error_message=f"Signal status is {signal.status}, not approved"
                )
            
            # Get symbol info
            symbol_info = mt5.symbol_info(signal.symbol)
            if symbol_info is None:
                return MT5ExecutionResult(
                    success=False,
                    error_message=f"Symbol {signal.symbol} not found"
                )
            
            # Enable symbol if not active
            if not symbol_info.visible:
                if not mt5.symbol_select(signal.symbol, True):
                    return MT5ExecutionResult(
                        success=False,
                        error_message=f"Failed to enable symbol {signal.symbol}"
                    )
            
            # Determine order type
            order_type = mt5.ORDER_TYPE_BUY if signal.direction == 'BUY' else mt5.ORDER_TYPE_SELL
            
            # Get current price
            tick = mt5.symbol_info_tick(signal.symbol)
            if tick is None:
                return MT5ExecutionResult(
                    success=False,
                    error_message=f"Failed to get tick data for {signal.symbol}"
                )
            
            # Use current market price for execution
            price = tick.ask if signal.direction == 'BUY' else tick.bid
            
            # Normalize volume
            normalized_volume = self._normalize_volume(signal.symbol, float(volume))
            
            # Normalize prices
            normalized_sl = self._normalize_price(signal.symbol, float(signal.stop_loss))
            normalized_tp = self._normalize_price(signal.symbol, float(signal.take_profit))
            
            # Create order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": signal.symbol,
                "volume": normalized_volume,
                "type": order_type,
                "price": price,
                "sl": normalized_sl,
                "tp": normalized_tp,
                "deviation": self.deviation,
                "magic": self.magic_number,
                "comment": f"MikroBot Signal {str(signal.id)[:8]}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result is None:
                return MT5ExecutionResult(
                    success=False,
                    error_message="Order send failed - no result"
                )
            
            # Check execution result
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return MT5ExecutionResult(
                    success=False,
                    error_code=result.retcode,
                    error_message=f"Order failed: {result.retcode} - {result.comment}"
                )
            
            # Success
            return MT5ExecutionResult(
                success=True,
                ticket=result.order,
                actual_entry_price=Decimal(str(result.price)),
                actual_volume=Decimal(str(result.volume)),
                execution_time=django_timezone.now()
            )
            
        except Exception as e:
            logger.error(f"MT5 execution error: {e}")
            return MT5ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    def close_trade(self, ticket: int) -> MT5ExecutionResult:
        """Close an open trade"""
        if not self.connected:
            if not self.connect():
                return MT5ExecutionResult(
                    success=False,
                    error_message="Failed to connect to MT5"
                )
        
        try:
            # Get position info
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return MT5ExecutionResult(
                    success=False,
                    error_message=f"Position {ticket} not found"
                )
            
            position = position[0]
            
            # Get current price
            tick = mt5.symbol_info_tick(position.symbol)
            if tick is None:
                return MT5ExecutionResult(
                    success=False,
                    error_message=f"Failed to get tick data for {position.symbol}"
                )
            
            # Determine close price and order type
            if position.type == mt5.POSITION_TYPE_BUY:
                price = tick.bid
                order_type = mt5.ORDER_TYPE_SELL
            else:
                price = tick.ask
                order_type = mt5.ORDER_TYPE_BUY
            
            # Create close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": self.deviation,
                "magic": self.magic_number,
                "comment": f"MikroBot Close {ticket}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            # Send close order
            result = mt5.order_send(request)
            
            if result is None:
                return MT5ExecutionResult(
                    success=False,
                    error_message="Close order failed - no result"
                )
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return MT5ExecutionResult(
                    success=False,
                    error_code=result.retcode,
                    error_message=f"Close failed: {result.retcode} - {result.comment}"
                )
            
            return MT5ExecutionResult(
                success=True,
                ticket=result.order,
                actual_entry_price=Decimal(str(result.price)),
                execution_time=django_timezone.now()
            )
            
        except Exception as e:
            logger.error(f"MT5 close error: {e}")
            return MT5ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    def get_position_info(self, ticket: int) -> Optional[Dict]:
        """Get current position information"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return None
            
            pos = position[0]
            return {
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'open_price': pos.price_open,
                'current_price': pos.price_current,
                'sl': pos.sl,
                'tp': pos.tp,
                'profit': pos.profit,
                'swap': pos.swap,
                'commission': pos.commission,
                'open_time': datetime.fromtimestamp(pos.time, tz=timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error getting position info: {e}")
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            account = mt5.account_info()
            if account is None:
                return None
            
            return {
                'login': account.login,
                'server': account.server,
                'currency': account.currency,
                'company': account.company,
                'balance': account.balance,
                'equity': account.equity,
                'margin': account.margin,
                'free_margin': account.margin_free,
                'margin_level': account.margin_level,
                'profit': account.profit
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def _normalize_volume(self, symbol: str, volume: float) -> float:
        """Normalize volume according to symbol requirements"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return volume
            
            # Check minimum volume
            if volume < symbol_info.volume_min:
                volume = symbol_info.volume_min
            
            # Check maximum volume
            if volume > symbol_info.volume_max:
                volume = symbol_info.volume_max
            
            # Round to volume step
            volume_step = symbol_info.volume_step
            if volume_step > 0:
                volume = round(volume / volume_step) * volume_step
            
            return volume
            
        except Exception as e:
            logger.error(f"Error normalizing volume: {e}")
            return volume
    
    def _normalize_price(self, symbol: str, price: float) -> float:
        """Normalize price according to symbol requirements"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return price
            
            # Round to tick size
            tick_size = symbol_info.point
            if tick_size > 0:
                digits = len(str(tick_size).split('.')[-1])
                price = round(price, digits)
            
            return price
            
        except Exception as e:
            logger.error(f"Error normalizing price: {e}")
            return price
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def execute_approved_signal(signal_id: str, volume: Decimal) -> Tuple[bool, str, Optional[int]]:
    """
    Convenience function to execute an approved signal
    Returns: (success, message, ticket)
    """
    try:
        signal = MQL5Signal.objects.get(id=signal_id)
        
        with MT5Executor() as executor:
            result = executor.execute_trade_from_signal(signal, volume)
            
            if result.success:
                # Mark signal as executed
                signal.status = 'executed'
                signal.save()
                
                return True, f"Trade executed successfully. Ticket: {result.ticket}", result.ticket
            else:
                return False, result.error_message or "Unknown error", None
                
    except MQL5Signal.DoesNotExist:
        return False, "Signal not found", None
    except Exception as e:
        logger.error(f"Error executing signal: {e}")
        return False, str(e), None


def close_trade_by_ticket(ticket: int) -> Tuple[bool, str]:
    """
    Convenience function to close a trade by ticket
    Returns: (success, message)
    """
    try:
        with MT5Executor() as executor:
            result = executor.close_trade(ticket)
            
            if result.success:
                return True, f"Trade {ticket} closed successfully"
            else:
                return False, result.error_message or "Unknown error"
                
    except Exception as e:
        logger.error(f"Error closing trade: {e}")
        return False, str(e)


def update_trade_from_mt5(trade: Trade) -> bool:
    """
    Update trade object with current MT5 position data
    """
    try:
        with MT5Executor() as executor:
            position_info = executor.get_position_info(trade.mt5_ticket)
            
            if position_info:
                # Update trade with current MT5 data
                trade.entry_price = Decimal(str(position_info['open_price']))
                trade.stop_loss = Decimal(str(position_info['sl'])) if position_info['sl'] > 0 else trade.stop_loss
                trade.take_profit = Decimal(str(position_info['tp'])) if position_info['tp'] > 0 else trade.take_profit
                trade.gross_profit_loss = Decimal(str(position_info['profit']))
                trade.swap = Decimal(str(position_info['swap']))
                trade.commission = Decimal(str(position_info['commission']))
                
                # Update status based on position
                if position_info['profit'] == 0:
                    trade.status = 'opened'
                elif position_info['profit'] > 0:
                    trade.status = 'opened'  # Still open, just profitable
                
                trade.save()
                return True
            else:
                # Position not found, might be closed
                trade.status = 'closed_unknown'
                trade.save()
                return False
                
    except Exception as e:
        logger.error(f"Error updating trade from MT5: {e}")
        return False