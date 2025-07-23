"""
# FROZEN VERSION 1.0 - FoxBox Framework™  
# Production-ready U-Cell Django serializers
# Last updated: 2025-07-23
# Status: PRODUCTION LOCKED 🔒

U-Cell Integration Serializers for Django
REST API serializers for U-Cell models
"""

from rest_framework import serializers
from .u_cell_models import (
    UCellSignalValidation,
    UCellRiskAssessment,
    UCellExecution,
    UCellQualityMeasurement,
    UCellProcessCapability,
    UCellSystemHealth
)


class UCellSignalValidationSerializer(serializers.ModelSerializer):
    """
    Serializer for U-Cell Signal Validation
    """
    
    mql5_signal_symbol = serializers.CharField(source='mql5_signal.symbol', read_only=True)
    mql5_signal_direction = serializers.CharField(source='mql5_signal.direction', read_only=True)
    
    class Meta:
        model = UCellSignalValidation
        fields = [
            'validation_id',
            'mql5_signal',
            'mql5_signal_symbol', 
            'mql5_signal_direction',
            'formatted_successfully',
            'poka_yoke_passed',
            'validation_errors',
            'bos_confirmed',
            'pip_movement',
            'confidence_score',
            'processing_time_ms',
            'correlation_id',
            'cpk_measurement',
            'created_at',
            'validated_at'
        ]
        read_only_fields = ['validation_id', 'created_at']


class UCellRiskAssessmentSerializer(serializers.ModelSerializer):
    """
    Serializer for U-Cell Risk Assessment
    """
    
    mql5_signal_symbol = serializers.CharField(source='mql5_signal.symbol', read_only=True)
    mql5_signal_direction = serializers.CharField(source='mql5_signal.direction', read_only=True)
    
    class Meta:
        model = UCellRiskAssessment
        fields = [
            'assessment_id',
            'mql5_signal',
            'mql5_signal_symbol',
            'mql5_signal_direction', 
            'approved',
            'position_size',
            'risk_amount',
            'risk_percentage',
            'daily_risk_used',
            'weekly_risk_used',
            'drawdown_impact',
            'calculation_accuracy',
            'processing_time_ms',
            'approval_reason',
            'rejection_reasons',
            'created_at',
            'assessed_at'
        ]
        read_only_fields = ['assessment_id', 'created_at']


class UCellExecutionSerializer(serializers.ModelSerializer):
    """
    Serializer for U-Cell Execution
    """
    
    mql5_signal_symbol = serializers.CharField(source='mql5_signal.symbol', read_only=True)
    mql5_signal_direction = serializers.CharField(source='mql5_signal.direction', read_only=True)
    trade_ticket = serializers.CharField(source='trade.mt5_ticket', read_only=True)
    
    class Meta:
        model = UCellExecution
        fields = [
            'execution_id',
            'mql5_signal',
            'mql5_signal_symbol',
            'mql5_signal_direction',
            'trade',
            'trade_ticket',
            'order_id',
            'requested_price',
            'executed_price',
            'slippage_pips',
            'stop_loss_order',
            'take_profit_order',
            'execution_status',
            'execution_quality',
            'mt5_response',
            'execution_latency_ms',
            'execution_notes',
            'created_at',
            'executed_at'
        ]
        read_only_fields = ['execution_id', 'created_at']


class UCellQualityMeasurementSerializer(serializers.ModelSerializer):
    """
    Serializer for U-Cell Quality Measurement
    """
    
    mql5_signal_symbol = serializers.CharField(source='mql5_signal.symbol', read_only=True)
    process_name_display = serializers.CharField(source='get_process_name_display', read_only=True)
    
    class Meta:
        model = UCellQualityMeasurement
        fields = [
            'measurement_id',
            'process_name',
            'process_name_display',
            'measurement_value',
            'measurement_unit',
            'target_value',
            'upper_spec_limit',
            'lower_spec_limit',
            'within_spec',
            'sigma_level',
            'mql5_signal',
            'mql5_signal_symbol',
            'correlation_id',
            'created_at'
        ]
        read_only_fields = ['measurement_id', 'within_spec', 'created_at']
    
    def validate(self, data):
        """
        Validate measurement data
        """
        if data['lower_spec_limit'] >= data['upper_spec_limit']:
            raise serializers.ValidationError(
                "Lower spec limit must be less than upper spec limit"
            )
        
        if not (data['lower_spec_limit'] <= data['target_value'] <= data['upper_spec_limit']):
            raise serializers.ValidationError(
                "Target value must be between spec limits"
            )
        
        return data


class UCellProcessCapabilitySerializer(serializers.ModelSerializer):
    """
    Serializer for U-Cell Process Capability
    """
    
    quality_status_display = serializers.CharField(source='get_quality_status_display', read_only=True)
    
    class Meta:
        model = UCellProcessCapability
        fields = [
            'capability_id',
            'process_name',
            'cp',
            'cpk',
            'pp',
            'ppk',
            'sigma_level',
            'dpmo',
            'mean',
            'std_dev',
            'sample_size',
            'quality_status',
            'quality_status_display',
            'meets_six_sigma',
            'measurement_period_hours',
            'analysis_timestamp',
            'recommendations',
            'created_at'
        ]
        read_only_fields = ['capability_id', 'created_at']


class UCellSystemHealthSerializer(serializers.ModelSerializer):
    """
    Serializer for U-Cell System Health
    """
    
    overall_status_display = serializers.CharField(source='get_overall_status_display', read_only=True)
    
    class Meta:
        model = UCellSystemHealth
        fields = [
            'health_id',
            'overall_status',
            'overall_status_display',
            'u_cell_status',
            'cp_cpk_metrics',
            'dpmo_current',
            'sigma_level',
            'system_latency',
            'throughput_rate',
            'error_rate',
            'uptime_percentage',
            'total_pnl',
            'win_rate',
            'sharpe_ratio',
            'max_drawdown',
            'created_at'
        ]
        read_only_fields = ['health_id', 'created_at']


class UCellIntegrationStatusSerializer(serializers.Serializer):
    """
    Serializer for overall U-Cell integration status
    """
    
    u_cell_1_status = serializers.CharField(read_only=True)
    u_cell_2_status = serializers.CharField(read_only=True)
    u_cell_3_status = serializers.CharField(read_only=True)
    u_cell_4_status = serializers.CharField(read_only=True)
    u_cell_5_status = serializers.CharField(read_only=True)
    
    overall_integration_status = serializers.CharField(read_only=True)
    
    total_signals_processed = serializers.IntegerField(read_only=True)
    total_validations_completed = serializers.IntegerField(read_only=True)
    total_risk_assessments = serializers.IntegerField(read_only=True)
    total_executions = serializers.IntegerField(read_only=True)
    total_quality_measurements = serializers.IntegerField(read_only=True)
    
    average_processing_time_ms = serializers.FloatField(read_only=True)
    system_uptime_percentage = serializers.FloatField(read_only=True)
    
    last_updated = serializers.DateTimeField(read_only=True)


class UCellSignalFlowSerializer(serializers.Serializer):
    """
    Serializer for complete signal flow through all U-Cells
    """
    
    signal_id = serializers.UUIDField(read_only=True)
    symbol = serializers.CharField(read_only=True)
    direction = serializers.CharField(read_only=True)
    
    # U-Cell 1: Signal Detection
    validation_status = serializers.CharField(read_only=True)
    validation_time_ms = serializers.FloatField(read_only=True)
    
    # U-Cell 2: Signal Reception (Django API)
    reception_status = serializers.CharField(read_only=True)
    
    # U-Cell 3: Processing & Analysis
    risk_assessment_status = serializers.CharField(read_only=True)
    position_size = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    risk_percentage = serializers.DecimalField(max_digits=5, decimal_places=3, read_only=True)
    
    # U-Cell 4: Execution
    execution_status = serializers.CharField(read_only=True)
    execution_time_ms = serializers.FloatField(read_only=True)
    slippage_pips = serializers.DecimalField(max_digits=8, decimal_places=1, read_only=True)
    
    # U-Cell 5: Monitoring & Control
    quality_measurements_count = serializers.IntegerField(read_only=True)
    
    # Overall flow
    total_processing_time_ms = serializers.FloatField(read_only=True)
    flow_status = serializers.CharField(read_only=True)
    
    created_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)