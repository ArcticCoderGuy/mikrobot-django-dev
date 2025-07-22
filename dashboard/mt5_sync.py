"""
MT5 Real-time trade synchronization
"""
import MetaTrader5 as mt5
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_mt5_live_trades():
    """
    Fetch ALL open positions from MT5 in real-time
    Returns formatted trade data for dashboard display
    """
    try:
        # Initialize MT5
        if not mt5.initialize():
            logger.error("MT5 initialization failed")
            return []
        
        # Get all open positions
        positions = mt5.positions_get()
        
        if positions is None:
            logger.warning("No positions found")
            return []
        
        trades = []
        for position in positions:
            # Calculate current P&L
            current_price = mt5.symbol_info_tick(position.symbol).bid if position.type == 0 else mt5.symbol_info_tick(position.symbol).ask
            
            # Calculate profit in pips
            if position.type == 0:  # BUY
                pips = (current_price - position.price_open) * 10000
            else:  # SELL
                pips = (position.price_open - current_price) * 10000
            
            trades.append({
                'id': position.ticket,
                'symbol': position.symbol,
                'type': 'BUY' if position.type == 0 else 'SELL',
                'volume': position.volume,
                'open_price': position.price_open,
                'current_price': current_price,
                'stop_loss': position.sl,
                'take_profit': position.tp,
                'profit': position.profit,
                'profit_pips': round(pips, 1),
                'status': 'opened',
                'open_time': datetime.fromtimestamp(position.time).strftime('%Y-%m-%d %H:%M:%S'),
                'comment': position.comment,
                'magic': position.magic,
                'source': 'MT5_LIVE'
            })
        
        # Sort by newest first
        trades.sort(key=lambda x: x['id'], reverse=True)
        
        return trades
        
    except Exception as e:
        logger.error(f"Error fetching MT5 trades: {e}")
        return []
    finally:
        mt5.shutdown()

def get_mt5_closed_trades(days=7):
    """
    Fetch closed trades from MT5 history
    Returns recent closed positions for dashboard display
    """
    try:
        # Initialize MT5
        if not mt5.initialize():
            logger.error("MT5 initialization failed")
            return []
        
        # Get deals from history (last 7 days)
        from datetime import datetime, timedelta
        date_from = datetime.now() - timedelta(days=days)
        date_to = datetime.now()
        
        # Get history deals
        deals = mt5.history_deals_get(date_from, date_to)
        
        if deals is None:
            logger.warning("No deals found in history")
            return []
        
        # Group deals by position to get complete trades
        position_deals = {}
        for deal in deals:
            if deal.position_id not in position_deals:
                position_deals[deal.position_id] = []
            position_deals[deal.position_id].append(deal)
        
        closed_trades = []
        for position_id, deal_list in position_deals.items():
            if len(deal_list) >= 2:  # Open + Close deal
                open_deal = min(deal_list, key=lambda x: x.time)
                close_deal = max(deal_list, key=lambda x: x.time)
                
                # Calculate duration
                duration_seconds = close_deal.time - open_deal.time
                duration_minutes = int(duration_seconds / 60)
                
                closed_trades.append({
                    'id': position_id,
                    'symbol': open_deal.symbol,
                    'type': 'BUY' if open_deal.type == 0 else 'SELL',
                    'volume': open_deal.volume,
                    'open_price': open_deal.price,
                    'close_price': close_deal.price,
                    'profit': close_deal.profit,
                    'open_time': datetime.fromtimestamp(open_deal.time).strftime('%Y-%m-%d %H:%M:%S'),
                    'close_time': datetime.fromtimestamp(close_deal.time).strftime('%Y-%m-%d %H:%M:%S'),
                    'duration_minutes': duration_minutes,
                    'comment': close_deal.comment,
                    'reason': 'SL' if 'sl' in close_deal.comment.lower() else 'TP' if 'tp' in close_deal.comment.lower() else 'Manual',
                    'source': 'MT5_HISTORY'
                })
        
        # Sort by close time (newest first)
        closed_trades.sort(key=lambda x: x['close_time'], reverse=True)
        
        return closed_trades[:20]  # Last 20 trades
        
    except Exception as e:
        logger.error(f"Error fetching MT5 closed trades: {e}")
        return []
    finally:
        mt5.shutdown()

def sync_mt5_to_dashboard():
    """
    Sync MT5 positions to Django Trade model
    """
    from trading.models import Trade
    
    try:
        mt5_trades = get_mt5_live_trades()
        
        for mt5_trade in mt5_trades:
            # Check if trade already exists
            trade, created = Trade.objects.get_or_create(
                mt5_ticket=mt5_trade['id'],
                defaults={
                    'symbol': mt5_trade['symbol'],
                    'action': mt5_trade['type'],
                    'volume': mt5_trade['volume'],
                    'entry_price': mt5_trade['open_price'],
                    'stop_loss': mt5_trade['stop_loss'],
                    'take_profit': mt5_trade['take_profit'],
                    'status': 'opened'
                }
            )
            
            # Update current price and profit
            if not created:
                trade.current_price = mt5_trade['current_price']
                trade.profit = mt5_trade['profit']
                trade.save()
                
        logger.info(f"Synced {len(mt5_trades)} trades from MT5")
        
    except Exception as e:
        logger.error(f"Error syncing MT5 trades: {e}")