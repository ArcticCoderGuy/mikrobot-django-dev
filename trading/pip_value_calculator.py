"""
Pip Value Calculator for MT5
Above Robust™ implementation - accurate pip value calculation
Created: 2025-07-23
"""

import MetaTrader5 as mt5
import logging
from decimal import Decimal
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class PipValueCalculator:
    """
    Calculate accurate pip values based on MT5 data
    No hardcoded values - everything from live market
    """
    
    def __init__(self, executor=None):
        """
        Initialize with optional MT5Executor instance
        """
        self.executor = executor
        self._pip_cache = {}  # Cache pip values for performance
        
    def calculate_pip_value(self, symbol: str, lot_size: float = 1.0, 
                          account_currency: str = None) -> Optional[float]:
        """
        Calculate pip value for given symbol and lot size
        
        Args:
            symbol: Trading symbol (e.g., 'EURUSD')
            lot_size: Lot size (default 1.0)
            account_currency: Account currency (if None, gets from MT5)
            
        Returns:
            Pip value in account currency, or None if calculation fails
        """
        try:
            # Use provided executor or create new connection
            if self.executor and self.executor.connected:
                return self._calculate_with_executor(
                    self.executor, symbol, lot_size, account_currency
                )
            else:
                from .mt5_executor import MT5Executor
                with MT5Executor() as executor:
                    return self._calculate_with_executor(
                        executor, symbol, lot_size, account_currency
                    )
                    
        except Exception as e:
            logger.error(f"Pip value calculation error for {symbol}: {e}")
            return None
    
    def _calculate_with_executor(self, executor, symbol: str, 
                                lot_size: float, account_currency: str) -> Optional[float]:
        """
        Calculate pip value using active MT5 connection
        """
        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found")
                return None
            
            # Get account currency if not provided
            if not account_currency:
                account_info = executor.get_account_info()
                if account_info:
                    account_currency = account_info['currency']
                else:
                    logger.error("Could not get account currency")
                    return None
            
            # Get current tick
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"No tick data for {symbol}")
                return None
            
            # Calculate based on symbol type
            pip_value = self._calculate_pip_value_internal(
                symbol_info, tick, lot_size, account_currency
            )
            
            if pip_value:
                # Cache the result
                cache_key = f"{symbol}_{lot_size}_{account_currency}"
                self._pip_cache[cache_key] = pip_value
                logger.debug(f"Pip value for {symbol}: {pip_value} {account_currency}")
            
            return pip_value
            
        except Exception as e:
            logger.error(f"Error in pip calculation: {e}")
            return None
    
    def _calculate_pip_value_internal(self, symbol_info, tick, 
                                    lot_size: float, account_currency: str) -> Optional[float]:
        """
        Internal pip value calculation logic
        """
        try:
            # Get contract size and point value
            contract_size = symbol_info.trade_contract_size
            point = symbol_info.point
            
            # Determine pip size (usually point * 10 for forex)
            if symbol_info.digits == 5 or symbol_info.digits == 3:
                pip_size = point * 10
            else:
                pip_size = point
            
            # Base and quote currencies
            base_currency = symbol_info.currency_base
            quote_currency = symbol_info.currency_profit
            
            # Case 1: Account currency is quote currency
            if account_currency == quote_currency:
                pip_value = (pip_size * contract_size * lot_size)
                return pip_value
            
            # Case 2: Account currency is base currency
            elif account_currency == base_currency:
                # Need current price
                current_price = tick.bid
                if current_price > 0:
                    pip_value = (pip_size * contract_size * lot_size) / current_price
                    return pip_value
            
            # Case 3: Cross currency calculation needed
            else:
                # Try to find conversion rate
                conversion_rate = self._get_conversion_rate(
                    quote_currency, account_currency
                )
                if conversion_rate:
                    pip_value = (pip_size * contract_size * lot_size) * conversion_rate
                    return pip_value
                else:
                    # Fallback to tick value method
                    return self._calculate_using_tick_value(
                        symbol_info.name, lot_size
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Internal calculation error: {e}")
            return None
    
    def _get_conversion_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Get conversion rate between currencies
        """
        try:
            # Direct rate
            direct_symbol = f"{from_currency}{to_currency}"
            symbol_info = mt5.symbol_info(direct_symbol)
            if symbol_info:
                tick = mt5.symbol_info_tick(direct_symbol)
                if tick:
                    return tick.bid
            
            # Inverse rate
            inverse_symbol = f"{to_currency}{from_currency}"
            symbol_info = mt5.symbol_info(inverse_symbol)
            if symbol_info:
                tick = mt5.symbol_info_tick(inverse_symbol)
                if tick and tick.bid > 0:
                    return 1.0 / tick.bid
            
            # USD cross rate
            if from_currency != 'USD' and to_currency != 'USD':
                rate1 = self._get_conversion_rate(from_currency, 'USD')
                rate2 = self._get_conversion_rate('USD', to_currency)
                if rate1 and rate2:
                    return rate1 * rate2
            
            return None
            
        except Exception as e:
            logger.error(f"Conversion rate error: {e}")
            return None
    
    def _calculate_using_tick_value(self, symbol: str, lot_size: float) -> Optional[float]:
        """
        Fallback method using MT5 tick value
        """
        try:
            # Get symbol tick value
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                # tick_value is profit for 1 lot when price changes by 1 tick
                tick_value = symbol_info.trade_tick_value
                
                # Calculate pip value (1 pip = 10 ticks for 5-digit symbols)
                if symbol_info.digits == 5 or symbol_info.digits == 3:
                    pip_value = tick_value * 10 * lot_size
                else:
                    pip_value = tick_value * lot_size
                
                return pip_value
            
            return None
            
        except Exception as e:
            logger.error(f"Tick value calculation error: {e}")
            return None
    
    def get_pip_values_for_symbols(self, symbols: list, lot_size: float = 1.0) -> Dict[str, float]:
        """
        Get pip values for multiple symbols
        """
        pip_values = {}
        
        from .mt5_executor import MT5Executor
        with MT5Executor() as executor:
            account_info = executor.get_account_info()
            account_currency = account_info['currency'] if account_info else 'USD'
            
            for symbol in symbols:
                pip_value = self._calculate_with_executor(
                    executor, symbol, lot_size, account_currency
                )
                if pip_value:
                    pip_values[symbol] = pip_value
        
        return pip_values
    
    def clear_cache(self):
        """
        Clear pip value cache
        """
        self._pip_cache.clear()


# Helper functions for quick access
def get_pip_value(symbol: str, lot_size: float = 1.0) -> Optional[float]:
    """
    Quick helper to get pip value for a symbol
    """
    calculator = PipValueCalculator()
    return calculator.calculate_pip_value(symbol, lot_size)


def get_pip_values_batch(symbols: list, lot_size: float = 1.0) -> Dict[str, float]:
    """
    Get pip values for multiple symbols in one MT5 connection
    """
    calculator = PipValueCalculator()
    return calculator.get_pip_values_for_symbols(symbols, lot_size)