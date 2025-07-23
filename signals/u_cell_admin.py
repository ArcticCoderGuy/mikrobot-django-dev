"""
U-Cell Integration Admin for Django
Admin interface for U-Cell models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .u_cell_models import (
    UCellSignalValidation,
    UCellRiskAssessment,
    UCellExecution,
    UCellQualityMeasurement,
    UCellProcessCapability,
    UCellSystemHealth
)


@admin.register(UCellSignalValidation)
class UCellSignalValidationAdmin(admin.ModelAdmin):
    """
    Admin for U-Cell Signal Validation
    """
    
    list_display = [
        'validation_id_short',
        'mql5_signal_link',
        'symbol',
        'direction',
        'validation_status',
        'confidence_score',
        'processing_time_ms',
        'created_at'
    ]
    
    list_filter = [
        'formatted_successfully',
        'poka_yoke_passed',
        'bos_confirmed',
        'mql5_signal__symbol',
        'mql5_signal__direction',
        'created_at'
    ]
    
    search_fields = [
        'validation_id',
        'mql5_signal__symbol',
        'correlation_id'
    ]
    
    readonly_fields = [
        'validation_id',
        'created_at',
        'validated_at',
        'validation_errors_display'
    ]
    
    fieldsets = (
        ('Signal Information', {
            'fields': ('mql5_signal', 'validation_id', 'correlation_id')
        }),
        ('Validation Results', {
            'fields': (
                'formatted_successfully',
                'poka_yoke_passed',
                'validation_errors_display',
                'bos_confirmed'
            )
        }),
        ('BOS Analysis', {
            'fields': ('pip_movement', 'confidence_score')
        }),
        ('Performance Metrics', {
            'fields': ('processing_time_ms', 'cpk_measurement')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'validated_at')
        })
    )
    
    def validation_id_short(self, obj):
        return str(obj.validation_id)[:8] + '...'
    validation_id_short.short_description = 'Validation ID'
    
    def mql5_signal_link(self, obj):
        url = reverse('admin:signals_mql5signal_change', args=[obj.mql5_signal.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.mql5_signal.pk)[:8])
    mql5_signal_link.short_description = 'Signal'
    
    def symbol(self, obj):
        return obj.mql5_signal.symbol
    
    def direction(self, obj):
        return obj.mql5_signal.direction
    
    def validation_status(self, obj):
        if obj.formatted_successfully and obj.poka_yoke_passed:
            return format_html('<span style="color: green;">✅ PASS</span>')
        else:
            return format_html('<span style="color: red;">❌ FAIL</span>')
    validation_status.short_description = 'Status'
    
    def validation_errors_display(self, obj):
        if not obj.validation_errors:
            return "No errors"
        
        html = "<ul>"
        for error in obj.validation_errors:
            html += f"<li><strong>{error.get('error_type', 'Unknown')}</strong>: {error.get('message', '')}</li>"
        html += "</ul>"
        return mark_safe(html)
    validation_errors_display.short_description = 'Validation Errors'


@admin.register(UCellRiskAssessment)
class UCellRiskAssessmentAdmin(admin.ModelAdmin):
    """
    Admin for U-Cell Risk Assessment
    """
    
    list_display = [
        'assessment_id_short',
        'mql5_signal_link',
        'symbol',
        'direction',
        'risk_status',
        'position_size',
        'risk_percentage_display',
        'created_at'
    ]
    
    list_filter = [
        'approved',
        'mql5_signal__symbol',
        'mql5_signal__direction',
        'created_at'
    ]
    
    search_fields = [
        'assessment_id',
        'mql5_signal__symbol'
    ]
    
    readonly_fields = [
        'assessment_id',
        'created_at',
        'assessed_at',
        'rejection_reasons_display'
    ]
    
    fieldsets = (
        ('Signal Information', {
            'fields': ('mql5_signal', 'assessment_id')
        }),
        ('Risk Assessment', {
            'fields': (
                'approved',
                'position_size',
                'risk_amount',
                'risk_percentage'
            )
        }),
        ('Risk Tracking', {
            'fields': (
                'daily_risk_used',
                'weekly_risk_used',
                'drawdown_impact'
            )
        }),
        ('Quality Metrics', {
            'fields': ('calculation_accuracy', 'processing_time_ms')
        }),
        ('Approval/Rejection', {
            'fields': ('approval_reason', 'rejection_reasons_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'assessed_at')
        })
    )
    
    def assessment_id_short(self, obj):
        return str(obj.assessment_id)[:8] + '...'
    assessment_id_short.short_description = 'Assessment ID'
    
    def mql5_signal_link(self, obj):
        url = reverse('admin:signals_mql5signal_change', args=[obj.mql5_signal.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.mql5_signal.pk)[:8])
    mql5_signal_link.short_description = 'Signal'
    
    def symbol(self, obj):
        return obj.mql5_signal.symbol
    
    def direction(self, obj):
        return obj.mql5_signal.direction
    
    def risk_status(self, obj):
        if obj.approved:
            return format_html('<span style="color: green;">✅ APPROVED</span>')
        else:
            return format_html('<span style="color: red;">❌ REJECTED</span>')
    risk_status.short_description = 'Status'
    
    def risk_percentage_display(self, obj):
        return f"{obj.risk_percentage:.2f}%"
    risk_percentage_display.short_description = 'Risk %'
    
    def rejection_reasons_display(self, obj):
        if not obj.rejection_reasons:
            return "None"
        
        html = "<ul>"
        for reason in obj.rejection_reasons:
            html += f"<li>{reason}</li>"
        html += "</ul>"
        return mark_safe(html)
    rejection_reasons_display.short_description = 'Rejection Reasons'


@admin.register(UCellExecution)
class UCellExecutionAdmin(admin.ModelAdmin):
    """
    Admin for U-Cell Execution
    """
    
    list_display = [
        'execution_id_short',
        'mql5_signal_link',
        'symbol',
        'direction',
        'execution_status_display',
        'order_id',
        'slippage_pips',
        'executed_at'
    ]
    
    list_filter = [
        'execution_status',
        'mql5_signal__symbol',
        'mql5_signal__direction',
        'created_at'
    ]
    
    search_fields = [
        'execution_id',
        'order_id',
        'mql5_signal__symbol'
    ]
    
    readonly_fields = [
        'execution_id',
        'created_at',
        'executed_at',
        'execution_quality_display',
        'mt5_response_display',
        'execution_notes_display'
    ]
    
    fieldsets = (
        ('Signal Information', {
            'fields': ('mql5_signal', 'trade', 'execution_id')
        }),
        ('Execution Details', {
            'fields': (
                'order_id',
                'execution_status',
                'requested_price',
                'executed_price',
                'slippage_pips'
            )
        }),
        ('Order Management', {
            'fields': ('stop_loss_order', 'take_profit_order')
        }),
        ('Quality & Response', {
            'fields': (
                'execution_quality_display',
                'mt5_response_display',
                'execution_latency_ms'
            )
        }),
        ('Notes & Timestamps', {
            'fields': ('execution_notes_display', 'created_at', 'executed_at')
        })
    )
    
    def execution_id_short(self, obj):
        return str(obj.execution_id)[:8] + '...'
    execution_id_short.short_description = 'Execution ID'
    
    def mql5_signal_link(self, obj):
        url = reverse('admin:signals_mql5signal_change', args=[obj.mql5_signal.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.mql5_signal.pk)[:8])
    mql5_signal_link.short_description = 'Signal'
    
    def symbol(self, obj):
        return obj.mql5_signal.symbol
    
    def direction(self, obj):
        return obj.mql5_signal.direction
    
    def execution_status_display(self, obj):
        status_colors = {
            'FILLED': 'green',
            'PENDING': 'orange',
            'PARTIAL': 'blue',
            'REJECTED': 'red',
            'FAILED': 'red'
        }
        color = status_colors.get(obj.execution_status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.execution_status
        )
    execution_status_display.short_description = 'Status'
    
    def execution_quality_display(self, obj):
        if not obj.execution_quality:
            return "No quality data"
        return mark_safe(f"<pre>{json.dumps(obj.execution_quality, indent=2)}</pre>")
    execution_quality_display.short_description = 'Execution Quality'
    
    def mt5_response_display(self, obj):
        if not obj.mt5_response:
            return "No MT5 response"
        return mark_safe(f"<pre>{json.dumps(obj.mt5_response, indent=2)}</pre>")
    mt5_response_display.short_description = 'MT5 Response'
    
    def execution_notes_display(self, obj):
        if not obj.execution_notes:
            return "No notes"
        
        html = "<ul>"
        for note in obj.execution_notes:
            html += f"<li>{note}</li>"
        html += "</ul>"
        return mark_safe(html)
    execution_notes_display.short_description = 'Execution Notes'


@admin.register(UCellQualityMeasurement)
class UCellQualityMeasurementAdmin(admin.ModelAdmin):
    """
    Admin for U-Cell Quality Measurement
    """
    
    list_display = [
        'measurement_id_short',
        'process_name',
        'measurement_value_display',
        'within_spec_display',
        'sigma_level',
        'mql5_signal_link',
        'created_at'
    ]
    
    list_filter = [
        'process_name',
        'within_spec',
        'measurement_unit',
        'created_at'
    ]
    
    search_fields = [
        'measurement_id',
        'process_name',
        'correlation_id',
        'mql5_signal__symbol'
    ]
    
    readonly_fields = ['measurement_id', 'within_spec', 'created_at']
    
    def measurement_id_short(self, obj):
        return str(obj.measurement_id)[:8] + '...'
    measurement_id_short.short_description = 'Measurement ID'
    
    def measurement_value_display(self, obj):
        return f"{obj.measurement_value} {obj.measurement_unit}"
    measurement_value_display.short_description = 'Value'
    
    def within_spec_display(self, obj):
        if obj.within_spec:
            return format_html('<span style="color: green;">✅ IN SPEC</span>')
        else:
            return format_html('<span style="color: red;">❌ OUT OF SPEC</span>')
    within_spec_display.short_description = 'Spec Compliance'
    
    def mql5_signal_link(self, obj):
        if obj.mql5_signal:
            url = reverse('admin:signals_mql5signal_change', args=[obj.mql5_signal.pk])
            return format_html('<a href="{}">{}</a>', url, str(obj.mql5_signal.pk)[:8])
        return "No signal"
    mql5_signal_link.short_description = 'Signal'


@admin.register(UCellProcessCapability)
class UCellProcessCapabilityAdmin(admin.ModelAdmin):
    """
    Admin for U-Cell Process Capability
    """
    
    list_display = [
        'process_name',
        'cpk_display',
        'sigma_level_display',
        'quality_status_display',
        'meets_six_sigma_display',
        'sample_size',
        'analysis_timestamp'
    ]
    
    list_filter = [
        'quality_status',
        'meets_six_sigma',
        'process_name',
        'analysis_timestamp'
    ]
    
    search_fields = ['process_name', 'capability_id']
    
    readonly_fields = [
        'capability_id',
        'created_at',
        'recommendations_display'
    ]
    
    def cpk_display(self, obj):
        color = 'green' if obj.cpk >= 2.0 else 'orange' if obj.cpk >= 1.33 else 'red'
        return format_html('<span style="color: {};">{:.3f}</span>', color, obj.cpk)
    cpk_display.short_description = 'Cpk'
    
    def sigma_level_display(self, obj):
        color = 'green' if obj.sigma_level >= 6.0 else 'orange' if obj.sigma_level >= 4.0 else 'red'
        return format_html('<span style="color: {};">{:.1f}σ</span>', color, obj.sigma_level)
    sigma_level_display.short_description = 'Sigma Level'
    
    def quality_status_display(self, obj):
        status_colors = {
            'EXCELLENT': 'green',
            'GOOD': 'blue',
            'MARGINAL': 'orange',
            'POOR': 'red'
        }
        color = status_colors.get(obj.quality_status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.quality_status)
    quality_status_display.short_description = 'Quality Status'
    
    def meets_six_sigma_display(self, obj):
        if obj.meets_six_sigma:
            return format_html('<span style="color: green;">✅ Six Sigma</span>')
        else:
            return format_html('<span style="color: red;">❌ Below Target</span>')
    meets_six_sigma_display.short_description = 'Six Sigma'
    
    def recommendations_display(self, obj):
        if not obj.recommendations:
            return "No recommendations"
        
        html = "<ul>"
        for rec in obj.recommendations:
            html += f"<li>{rec}</li>"
        html += "</ul>"
        return mark_safe(html)
    recommendations_display.short_description = 'Recommendations'


@admin.register(UCellSystemHealth)
class UCellSystemHealthAdmin(admin.ModelAdmin):
    """
    Admin for U-Cell System Health
    """
    
    list_display = [
        'overall_status_display',
        'sigma_level_display',
        'throughput_rate',
        'error_rate_display',
        'uptime_percentage_display',
        'created_at'
    ]
    
    list_filter = [
        'overall_status',
        'created_at'
    ]
    
    readonly_fields = [
        'health_id',
        'created_at',
        'u_cell_status_display',
        'cp_cpk_metrics_display',
        'system_latency_display'
    ]
    
    fieldsets = (
        ('Overall Health', {
            'fields': ('health_id', 'overall_status', 'created_at')
        }),
        ('U-Cell Status', {
            'fields': ('u_cell_status_display',)
        }),
        ('Six Sigma Metrics', {
            'fields': (
                'cp_cpk_metrics_display',
                'dpmo_current',
                'sigma_level'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'system_latency_display',
                'throughput_rate',
                'error_rate',
                'uptime_percentage'
            )
        }),
        ('Financial Metrics', {
            'fields': (
                'total_pnl',
                'win_rate',
                'sharpe_ratio',
                'max_drawdown'
            )
        })
    )
    
    def overall_status_display(self, obj):
        status_colors = {
            'HEALTHY': 'green',
            'WARNING': 'orange',
            'CRITICAL': 'red',
            'DOWN': 'darkred'
        }
        color = status_colors.get(obj.overall_status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.overall_status)
    overall_status_display.short_description = 'Status'
    
    def sigma_level_display(self, obj):
        color = 'green' if obj.sigma_level >= 6.0 else 'orange' if obj.sigma_level >= 4.0 else 'red'
        return format_html('<span style="color: {};">{:.1f}σ</span>', color, obj.sigma_level)
    sigma_level_display.short_description = 'Sigma Level'
    
    def error_rate_display(self, obj):
        color = 'green' if obj.error_rate <= 0.01 else 'orange' if obj.error_rate <= 0.05 else 'red'
        return format_html('<span style="color: {};">{:.2%}</span>', color, obj.error_rate)
    error_rate_display.short_description = 'Error Rate'
    
    def uptime_percentage_display(self, obj):
        color = 'green' if obj.uptime_percentage >= 99.9 else 'orange' if obj.uptime_percentage >= 99.0 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, obj.uptime_percentage)
    uptime_percentage_display.short_description = 'Uptime'
    
    def u_cell_status_display(self, obj):
        if not obj.u_cell_status:
            return "No U-Cell status data"
        return mark_safe(f"<pre>{json.dumps(obj.u_cell_status, indent=2)}</pre>")
    u_cell_status_display.short_description = 'U-Cell Status'
    
    def cp_cpk_metrics_display(self, obj):
        if not obj.cp_cpk_metrics:
            return "No Cp/Cpk metrics"
        return mark_safe(f"<pre>{json.dumps(obj.cp_cpk_metrics, indent=2)}</pre>")
    cp_cpk_metrics_display.short_description = 'Cp/Cpk Metrics'
    
    def system_latency_display(self, obj):
        if not obj.system_latency:
            return "No latency data"
        return mark_safe(f"<pre>{json.dumps(obj.system_latency, indent=2)}</pre>")
    system_latency_display.short_description = 'System Latency'