from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from decimal import Decimal
from .models import Trade, TradingSession
from .serializers import (
    TradeSerializer, 
    TradeCreateSerializer, 
    TradeUpdateSerializer,
    TradingSessionSerializer,
    SignalToTradeSerializer
)
from .mt5_executor import (
    MT5Executor, 
    execute_approved_signal, 
    close_trade_by_ticket,
    update_trade_from_mt5
)

class TradeViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Trade management
    """
    
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    
    # Enable filtering and searching (disabled DjangoFilterBackend for Python 3.13 compatibility)
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['status', 'direction', 'symbol', 'exit_reason']
    filter_backends = [SearchFilter, OrderingFilter]  # Only basic filters
    search_fields = ['symbol', 'mt5_ticket', 'notes']
    ordering_fields = ['execution_time', 'close_time', 'net_profit_loss']
    ordering = ['-execution_time']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return TradeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TradeUpdateSerializer
        elif self.action == 'create_from_signal':
            return SignalToTradeSerializer
        return TradeSerializer
    
    @action(detail=False, methods=['get'])
    def active_trades(self, request):
        """Get all active (opened) trades"""
        active_trades = self.get_queryset().filter(status='opened')
        serializer = self.get_serializer(active_trades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent_trades(self, request):
        """Get recent trades (last 50)"""
        recent_trades = self.get_queryset()[:50]
        serializer = self.get_serializer(recent_trades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def profitable_trades(self, request):
        """Get all profitable trades"""
        profitable_trades = self.get_queryset().filter(
            status__in=['closed_profit', 'closed_breakeven'],
            net_profit_loss__gt=0
        )
        serializer = self.get_serializer(profitable_trades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def losing_trades(self, request):
        """Get all losing trades"""
        losing_trades = self.get_queryset().filter(
            status='closed_loss',
            net_profit_loss__lt=0
        )
        serializer = self.get_serializer(losing_trades, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close_trade(self, request, pk=None):
        """Close an active trade"""
        trade = self.get_object()
        
        if trade.status != 'opened':
            return Response(
                {'error': 'Only opened trades can be closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Required fields for closing
        exit_price = request.data.get('exit_price')
        exit_reason = request.data.get('exit_reason', 'manual')
        gross_pnl = request.data.get('gross_profit_loss')
        
        if not exit_price:
            return Response(
                {'error': 'exit_price is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update trade
        trade.exit_price = exit_price
        trade.exit_reason = exit_reason
        trade.close_time = timezone.now()
        trade.commission = request.data.get('commission', 0)
        trade.swap = request.data.get('swap', 0)
        trade.max_drawdown = request.data.get('max_drawdown')
        trade.max_profit = request.data.get('max_profit')
        
        if gross_pnl is not None:
            trade.gross_profit_loss = gross_pnl
        
        # Determine final status
        if trade.net_profit_loss > 0:
            trade.status = 'closed_profit'
        elif trade.net_profit_loss < 0:
            trade.status = 'closed_loss'
        else:
            trade.status = 'closed_breakeven'
        
        trade.save()
        
        return Response({
            'message': 'Trade closed successfully',
            'trade_id': str(trade.id),
            'final_status': trade.status,
            'pnl': float(trade.net_profit_loss) if trade.net_profit_loss else 0,
            'pips': trade.calculate_pips()
        })
    
    @action(detail=False, methods=['post'])
    def create_from_signal(self, request):
        """Create trade from approved signal"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            trade = serializer.save()
            
            return Response({
                'message': 'Trade created from signal successfully',
                'trade_id': str(trade.id),
                'signal_id': str(trade.mql5_signal.id),
                'status': trade.status
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get comprehensive trading statistics"""
        queryset = self.get_queryset()
        
        # Basic counts
        total_trades = queryset.count()
        active_trades = queryset.filter(status='opened').count()
        closed_trades = queryset.filter(status__startswith='closed_').count()
        
        # P&L statistics
        total_pnl = queryset.aggregate(
            total=Sum('net_profit_loss')
        )['total'] or 0
        
        profitable_trades = queryset.filter(
            net_profit_loss__gt=0,
            status__startswith='closed_'
        )
        losing_trades = queryset.filter(
            net_profit_loss__lt=0,
            status__startswith='closed_'
        )
        
        # Performance metrics
        win_rate = 0
        if closed_trades > 0:
            win_rate = (profitable_trades.count() / closed_trades) * 100
        
        # Average trade metrics
        avg_profit = profitable_trades.aggregate(
            avg=Avg('net_profit_loss')
        )['avg'] or 0
        
        avg_loss = losing_trades.aggregate(
            avg=Avg('net_profit_loss')
        )['avg'] or 0
        
        # Symbol breakdown
        symbol_stats = queryset.values('symbol').annotate(
            count=Count('id'),
            pnl=Sum('net_profit_loss')
        ).order_by('-count')
        
        # Direction breakdown
        direction_stats = queryset.values('direction').annotate(
            count=Count('id'),
            pnl=Sum('net_profit_loss')
        )
        
        return Response({
            'total_trades': total_trades,
            'active_trades': active_trades,
            'closed_trades': closed_trades,
            'total_pnl': float(total_pnl),
            'win_rate': round(win_rate, 2),
            'profitable_trades': profitable_trades.count(),
            'losing_trades': losing_trades.count(),
            'average_profit': float(avg_profit),
            'average_loss': float(avg_loss),
            'symbol_breakdown': list(symbol_stats),
            'direction_breakdown': list(direction_stats)
        })
    
    @action(detail=False, methods=['post'])
    def bulk_close(self, request):
        """Bulk close multiple trades"""
        trade_ids = request.data.get('trade_ids', [])
        exit_reason = request.data.get('exit_reason', 'bulk_close')
        
        if not trade_ids:
            return Response(
                {'error': 'trade_ids list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get active trades
        active_trades = self.get_queryset().filter(
            id__in=trade_ids,
            status='opened'
        )
        
        closed_count = 0
        for trade in active_trades:
            # This would typically get current market price
            # For now, we'll mark as cancelled
            trade.status = 'cancelled'
            trade.exit_reason = exit_reason
            trade.close_time = timezone.now()
            trade.save()
            closed_count += 1
        
        return Response({
            'message': f'{closed_count} trades closed successfully',
            'closed_count': closed_count
        })
    
    @action(detail=False, methods=['post'])
    def execute_signal(self, request):
        """Execute approved signal via MT5"""
        signal_id = request.data.get('signal_id')
        volume = request.data.get('volume', 0.01)
        
        if not signal_id:
            return Response(
                {'error': 'signal_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            print(f"DEBUG: volume = {volume}, type = {type(volume)}")
            volume = Decimal(str(volume))
            print(f"DEBUG: Decimal conversion successful: {volume}")
        except Exception as e:
            print(f"DEBUG: Decimal conversion failed: {e}")
            return Response(
                {'error': f'Invalid volume format: {volume} (type: {type(volume)})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Execute signal
        success, message, ticket = execute_approved_signal(signal_id, volume)
        
        if success:
            # Create trade record
            from signals.models import MQL5Signal
            signal = MQL5Signal.objects.get(id=signal_id)
            
            trade = Trade.objects.create(
                mql5_signal=signal,
                mt5_ticket=ticket,
                mt5_order_type=f"ORDER_TYPE_{signal.direction}",
                symbol=signal.symbol,
                direction=signal.direction,
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                volume=volume,
                signal_time=signal.signal_timestamp,
                execution_time=timezone.now(),
                status='opened'
            )
            
            return Response({
                'message': message,
                'trade_id': str(trade.id),
                'mt5_ticket': ticket,
                'signal_id': signal_id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def close_mt5_trade(self, request, pk=None):
        """Close trade via MT5"""
        trade = self.get_object()
        
        if trade.status != 'opened':
            return Response(
                {'error': 'Only opened trades can be closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Close trade in MT5
        success, message = close_trade_by_ticket(trade.mt5_ticket)
        
        if success:
            # Update trade status
            trade.status = 'closed_profit'  # Will be updated by sync
            trade.close_time = timezone.now()
            trade.exit_reason = 'manual'
            trade.save()
            
            return Response({
                'message': message,
                'trade_id': str(trade.id),
                'mt5_ticket': trade.mt5_ticket
            })
        else:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def sync_with_mt5(self, request, pk=None):
        """Sync trade with MT5 position data"""
        trade = self.get_object()
        
        if trade.status not in ['opened', 'pending']:
            return Response(
                {'error': 'Trade is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update from MT5
        success = update_trade_from_mt5(trade)
        
        if success:
            # Refresh from database
            trade.refresh_from_db()
            serializer = self.get_serializer(trade)
            
            return Response({
                'message': 'Trade synchronized successfully',
                'trade': serializer.data
            })
        else:
            return Response(
                {'error': 'Failed to sync with MT5'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def mt5_account_info(self, request):
        """Get MT5 account information"""
        try:
            with MT5Executor() as executor:
                account_info = executor.get_account_info()
                
                if account_info:
                    return Response(account_info)
                else:
                    return Response(
                        {'error': 'Failed to get account info'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_sync_mt5(self, request):
        """Bulk sync all active trades with MT5"""
        active_trades = self.get_queryset().filter(status='opened')
        
        results = []
        for trade in active_trades:
            try:
                success = update_trade_from_mt5(trade)
                results.append({
                    'trade_id': str(trade.id),
                    'mt5_ticket': trade.mt5_ticket,
                    'success': success
                })
            except Exception as e:
                results.append({
                    'trade_id': str(trade.id),
                    'mt5_ticket': trade.mt5_ticket,
                    'success': False,
                    'error': str(e)
                })
        
        return Response({
            'message': f'Synced {len(results)} trades',
            'results': results
        })


class TradingSessionViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Trading Session management
    """
    
    queryset = TradingSession.objects.all()
    serializer_class = TradingSessionSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['session_name']
    search_fields = ['session_name']
    ordering_fields = ['start_time', 'total_pnl']
    ordering = ['-start_time']
    
    @action(detail=True, methods=['post'])
    def add_trades(self, request, pk=None):
        """Add trades to trading session"""
        session = self.get_object()
        trade_ids = request.data.get('trade_ids', [])
        
        if not trade_ids:
            return Response(
                {'error': 'trade_ids list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get valid trades
        trades = Trade.objects.filter(id__in=trade_ids)
        
        # Add trades to session
        session.trades.add(*trades)
        
        # Update session statistics
        session.total_trades = session.trades.count()
        session.winning_trades = session.trades.filter(
            net_profit_loss__gt=0
        ).count()
        session.losing_trades = session.trades.filter(
            net_profit_loss__lt=0
        ).count()
        session.total_pnl = session.trades.aggregate(
            total=Sum('net_profit_loss')
        )['total'] or 0
        
        session.save()
        
        return Response({
            'message': f'{trades.count()} trades added to session',
            'session_id': session.id,
            'total_trades': session.total_trades
        })
    
    @action(detail=False, methods=['get'])
    def active_session(self, request):
        """Get current active trading session"""
        now = timezone.now()
        active_session = self.get_queryset().filter(
            start_time__lte=now,
            end_time__gte=now
        ).first()
        
        if active_session:
            serializer = self.get_serializer(active_session)
            return Response(serializer.data)
        else:
            return Response(
                {'message': 'No active trading session'},
                status=status.HTTP_404_NOT_FOUND
            )
