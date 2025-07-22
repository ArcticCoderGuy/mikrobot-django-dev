from rest_framework import serializers
from django.db import models
from .models import Trade, TradingSession
from signals.models import MQL5Signal

class TradeSerializer(serializers.ModelSerializer):
    """
    Serializer for Trade model
    """
    
    pips_gained = serializers.SerializerMethodField()
    is_profitable = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Trade
        fields = [
            'id',
            'mql5_signal',
            'mt5_ticket',
            'mt5_order_type',
            'symbol',
            'direction',
            'entry_price',
            'exit_price',
            'stop_loss',
            'take_profit',
            'volume',
            'status',
            'gross_profit_loss',
            'commission',
            'swap',
            'net_profit_loss',
            'signal_time',
            'execution_time',
            'close_time',
            'duration_minutes',
            'max_drawdown',
            'max_profit',
            'exit_reason',
            'django_decision_time',
            'execution_delay_seconds',
            'notes',
            'pips_gained',
            'is_profitable',
            'duration_hours'
        ]
        read_only_fields = [
            'id', 'django_decision_time', 'net_profit_loss',
            'duration_minutes', 'execution_delay_seconds',
            'pips_gained', 'is_profitable', 'duration_hours'
        ]
    
    def get_pips_gained(self, obj):
        """Calculate pips gained/lost"""
        return obj.calculate_pips()
    
    def get_is_profitable(self, obj):
        """Check if trade is profitable"""
        return obj.is_profitable()
    
    def get_duration_hours(self, obj):
        """Convert duration to hours"""
        if obj.duration_minutes:
            return round(obj.duration_minutes / 60.0, 2)
        return None


class TradeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new trades
    """
    
    class Meta:
        model = Trade
        fields = [
            'mql5_signal',
            'mt5_ticket',
            'mt5_order_type',
            'symbol',
            'direction',
            'entry_price',
            'stop_loss',
            'take_profit',
            'volume',
            'signal_time',
            'execution_time',
            'notes'
        ]
    
    def create(self, validated_data):
        """Create trade with pending status"""
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class TradeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating trade status and results
    """
    
    class Meta:
        model = Trade
        fields = [
            'status',
            'exit_price',
            'gross_profit_loss',
            'commission',
            'swap',
            'close_time',
            'max_drawdown',
            'max_profit',
            'exit_reason',
            'notes'
        ]
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            current_status = self.instance.status
            
            # Define allowed transitions
            allowed_transitions = {
                'pending': ['opened', 'cancelled', 'error'],
                'opened': ['closed_profit', 'closed_loss', 'closed_breakeven', 'cancelled'],
                'closed_profit': [],  # Final state
                'closed_loss': [],    # Final state
                'closed_breakeven': [],  # Final state
                'cancelled': ['pending'],  # Allow retry
                'error': ['pending']      # Allow retry
            }
            
            if value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot transition from {current_status} to {value}"
                )
        
        return value
    
    def validate(self, data):
        """Custom validation for trade updates"""
        # If closing trade, require exit price
        status = data.get('status')
        if status and status.startswith('closed_') and not data.get('exit_price'):
            raise serializers.ValidationError(
                "Exit price is required when closing a trade"
            )
        
        # If marking as error, require notes
        if status == 'error' and not data.get('notes'):
            raise serializers.ValidationError(
                "Notes are required when marking trade as error"
            )
        
        return data


class TradingSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for Trading Session
    """
    
    win_rate = serializers.SerializerMethodField()
    total_pips = serializers.SerializerMethodField()
    average_trade_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = TradingSession
        fields = [
            'id',
            'session_name',
            'start_time',
            'end_time',
            'total_trades',
            'winning_trades',
            'losing_trades',
            'total_pnl',
            'max_concurrent_trades',
            'max_drawdown_session',
            'trades',
            'win_rate',
            'total_pips',
            'average_trade_duration'
        ]
    
    def get_win_rate(self, obj):
        """Calculate win rate"""
        return obj.win_rate()
    
    def get_total_pips(self, obj):
        """Calculate total pips from all trades"""
        total_pips = 0
        for trade in obj.trades.all():
            pips = trade.calculate_pips()
            if pips is not None:
                total_pips += pips
        return total_pips
    
    def get_average_trade_duration(self, obj):
        """Calculate average trade duration in hours"""
        trades = obj.trades.filter(duration_minutes__isnull=False)
        if trades.exists():
            avg_minutes = trades.aggregate(avg=models.Avg('duration_minutes'))['avg']
            return round(avg_minutes / 60.0, 2) if avg_minutes else 0
        return 0


class SignalToTradeSerializer(serializers.Serializer):
    """
    Serializer for converting approved signals to trades
    """
    
    signal_id = serializers.UUIDField()
    mt5_ticket = serializers.IntegerField()
    mt5_order_type = serializers.CharField(max_length=20)
    volume = serializers.DecimalField(max_digits=8, decimal_places=2)
    execution_time = serializers.DateTimeField()
    actual_entry_price = serializers.DecimalField(max_digits=10, decimal_places=5, required=False)
    actual_stop_loss = serializers.DecimalField(max_digits=10, decimal_places=5, required=False)
    actual_take_profit = serializers.DecimalField(max_digits=10, decimal_places=5, required=False)
    notes = serializers.CharField(max_length=500, required=False)
    
    def validate_signal_id(self, value):
        """Validate signal exists and is approved"""
        try:
            signal = MQL5Signal.objects.get(id=value)
            if signal.status != 'approved':
                raise serializers.ValidationError(
                    f"Signal status is {signal.status}, not approved"
                )
            
            # Check if trade already exists
            if hasattr(signal, 'trade'):
                raise serializers.ValidationError(
                    "Trade already exists for this signal"
                )
            
            return value
        except MQL5Signal.DoesNotExist:
            raise serializers.ValidationError("Signal not found")
    
    def create(self, validated_data):
        """Create trade from approved signal"""
        signal_id = validated_data.pop('signal_id')
        signal = MQL5Signal.objects.get(id=signal_id)
        
        # Create trade from signal
        trade = Trade.objects.create(
            mql5_signal=signal,
            mt5_ticket=validated_data['mt5_ticket'],
            mt5_order_type=validated_data['mt5_order_type'],
            symbol=signal.symbol,
            direction=signal.direction,
            entry_price=validated_data.get('actual_entry_price', signal.entry_price),
            stop_loss=validated_data.get('actual_stop_loss', signal.stop_loss),
            take_profit=validated_data.get('actual_take_profit', signal.take_profit),
            volume=validated_data['volume'],
            signal_time=signal.signal_timestamp,
            execution_time=validated_data['execution_time'],
            status='opened',
            notes=validated_data.get('notes', '')
        )
        
        # Mark signal as executed
        signal.status = 'executed'
        signal.save()
        
        return trade