"""
# FROZEN VERSION 1.0 - FoxBox Framework™
# Production-ready U-Cell Django models  
# Last updated: 2025-07-23
# Status: PRODUCTION LOCKED 🔒

U-Cell Integration Models for Django
Extends existing Django models with U-Cell specific functionality
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import json


class UCellSignalValidation(models.Model):
    """
    U-Cell 1: Signal Detection - Validation Results
    Links to MQL5Signal with additional U-Cell validation data
    """
    
    # Link to original signal
    mql5_signal = models.OneToOneField(
        'signals.MQL5Signal', 
        on_delete=models.CASCADE,
        related_name='u_cell_validation'
    )
    
    # U-Cell validation results
    validation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Signal formatting results
    formatted_successfully = models.BooleanField(default=False)
    poka_yoke_passed = models.BooleanField(default=False)
    validation_errors = models.JSONField(default=list, blank=True)
    
    # BOS specific validation
    bos_confirmed = models.BooleanField(default=False)
    pip_movement = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    # Processing metrics
    processing_time_ms = models.FloatField(null=True, blank=True)
    correlation_id = models.CharField(max_length=100, blank=True)
    
    # Quality metrics
    cpk_measurement = models.FloatField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "U-Cell Signal Validation"
        verbose_name_plural = "U-Cell Signal Validations"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"U-Cell Validation: {self.mql5_signal.symbol} ({self.validation_id})"


class UCellRiskAssessment(models.Model):
    """
    U-Cell 3: Processing & Analysis - Risk Assessment Results
    """
    
    # Link to signal
    mql5_signal = models.OneToOneField(
        'signals.MQL5Signal',
        on_delete=models.CASCADE,
        related_name='u_cell_risk'
    )
    
    # Risk calculation results
    assessment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    approved = models.BooleanField(default=False)
    
    # Position sizing
    position_size = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    risk_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    risk_percentage = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    
    # Risk tracking
    daily_risk_used = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    weekly_risk_used = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    drawdown_impact = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    
    # Quality metrics
    calculation_accuracy = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    processing_time_ms = models.FloatField(default=0)
    
    # Approval/rejection
    approval_reason = models.TextField(blank=True)
    rejection_reasons = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    assessed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "U-Cell Risk Assessment"
        verbose_name_plural = "U-Cell Risk Assessments"
        ordering = ['-created_at']
    
    def __str__(self):
        status = "APPROVED" if self.approved else "REJECTED"
        return f"Risk {status}: {self.mql5_signal.symbol} - {self.position_size} lots"


class UCellExecution(models.Model):
    """
    U-Cell 4: Execution - Order Execution Results
    """
    
    # Link to signal and trade
    mql5_signal = models.OneToOneField(
        'signals.MQL5Signal',
        on_delete=models.CASCADE,
        related_name='u_cell_execution'
    )
    
    trade = models.OneToOneField(
        'trading.Trade',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='u_cell_execution'
    )
    
    # Execution results
    execution_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order_id = models.CharField(max_length=50, blank=True)
    
    # Execution details
    requested_price = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    executed_price = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    slippage_pips = models.DecimalField(max_digits=8, decimal_places=1, default=0)
    
    # Order management
    stop_loss_order = models.CharField(max_length=50, blank=True)
    take_profit_order = models.CharField(max_length=50, blank=True)
    
    # Status and quality
    EXECUTION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('FILLED', 'Filled'),
        ('PARTIAL', 'Partial'),
        ('REJECTED', 'Rejected'),
        ('FAILED', 'Failed'),
    ]
    
    execution_status = models.CharField(
        max_length=20, 
        choices=EXECUTION_STATUS_CHOICES,
        default='PENDING'
    )
    
    execution_quality = models.JSONField(default=dict, blank=True)
    mt5_response = models.JSONField(default=dict, blank=True)
    
    # Performance metrics
    execution_latency_ms = models.FloatField(default=0)
    execution_notes = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "U-Cell Execution"
        verbose_name_plural = "U-Cell Executions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Execution {self.execution_status}: {self.mql5_signal.symbol} ({self.order_id})"


class UCellQualityMeasurement(models.Model):
    """
    U-Cell 5: Monitoring & Control - Quality Measurements
    """
    
    # Measurement details
    measurement_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    PROCESS_CHOICES = [
        ('signal_processing_latency', 'Signal Processing Latency'),
        ('risk_calculation_accuracy', 'Risk Calculation Accuracy'),
        ('order_execution_slippage', 'Order Execution Slippage'),
        ('kafka_delivery_success', 'Kafka Delivery Success'),
        ('end_to_end_latency', 'End-to-End Latency'),
    ]
    
    process_name = models.CharField(max_length=50, choices=PROCESS_CHOICES)
    measurement_value = models.FloatField()
    measurement_unit = models.CharField(max_length=20)
    
    # Target and limits
    target_value = models.FloatField()
    upper_spec_limit = models.FloatField()
    lower_spec_limit = models.FloatField()
    
    # Quality assessment
    within_spec = models.BooleanField(default=True)
    sigma_level = models.FloatField(null=True, blank=True)
    
    # Links to source
    mql5_signal = models.ForeignKey(
        'signals.MQL5Signal',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='quality_measurements'
    )
    
    correlation_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "U-Cell Quality Measurement"
        verbose_name_plural = "U-Cell Quality Measurements"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['process_name', 'created_at']),
            models.Index(fields=['correlation_id']),
        ]
    
    def __str__(self):
        return f"{self.process_name}: {self.measurement_value}{self.measurement_unit}"


class UCellProcessCapability(models.Model):
    """
    U-Cell 5: Monitoring & Control - Process Capability Analysis
    """
    
    # Analysis details
    capability_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    process_name = models.CharField(max_length=50)
    
    # Capability indices
    cp = models.FloatField(help_text="Process capability")
    cpk = models.FloatField(help_text="Process capability index") 
    pp = models.FloatField(help_text="Process performance")
    ppk = models.FloatField(help_text="Process performance index")
    
    # Statistics
    sigma_level = models.FloatField()
    dpmo = models.FloatField(help_text="Defects per million opportunities")
    mean = models.FloatField()
    std_dev = models.FloatField()
    sample_size = models.IntegerField()
    
    # Quality assessment
    QUALITY_STATUS_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'), 
        ('MARGINAL', 'Marginal'),
        ('POOR', 'Poor'),
    ]
    
    quality_status = models.CharField(max_length=20, choices=QUALITY_STATUS_CHOICES)
    meets_six_sigma = models.BooleanField(default=False)
    
    # Analysis period
    measurement_period_hours = models.FloatField()
    analysis_timestamp = models.DateTimeField()
    
    # Recommendations
    recommendations = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "U-Cell Process Capability"
        verbose_name_plural = "U-Cell Process Capabilities"
        ordering = ['-analysis_timestamp']
    
    def __str__(self):
        return f"{self.process_name}: Cpk={self.cpk:.3f}, σ={self.sigma_level:.1f}"


class UCellSystemHealth(models.Model):
    """
    U-Cell 5: Monitoring & Control - Overall System Health Status
    """
    
    # Health status
    health_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    HEALTH_STATUS_CHOICES = [
        ('HEALTHY', 'Healthy'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
        ('DOWN', 'Down'),
    ]
    
    overall_status = models.CharField(max_length=20, choices=HEALTH_STATUS_CHOICES)
    
    # U-Cell health
    u_cell_status = models.JSONField(default=dict, help_text="Each U-Cell health status")
    
    # Six Sigma metrics
    cp_cpk_metrics = models.JSONField(default=dict, help_text="Cp/Cpk for each process")
    dpmo_current = models.FloatField(default=0)
    sigma_level = models.FloatField(default=0)
    
    # Performance summary
    system_latency = models.JSONField(default=dict, help_text="P50, P95, P99 latencies")
    throughput_rate = models.FloatField(default=0, help_text="Signals per hour")
    error_rate = models.FloatField(default=0, help_text="Overall error rate")
    uptime_percentage = models.FloatField(default=0)
    
    # Financial metrics  
    total_pnl = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    win_rate = models.FloatField(default=0)
    sharpe_ratio = models.FloatField(default=0)
    max_drawdown = models.FloatField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "U-Cell System Health"  
        verbose_name_plural = "U-Cell System Health"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"System Health: {self.overall_status} (σ={self.sigma_level:.1f})"