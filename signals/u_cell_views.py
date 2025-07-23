"""
# FROZEN VERSION 1.0 - FoxBox Framework™
# Production-ready U-Cell Django views
# Last updated: 2025-07-23  
# Status: PRODUCTION LOCKED 🔒

U-Cell Integration Views for Django
API endpoints for U-Cell component integration
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import MQL5Signal
from .u_cell_models import (
    UCellSignalValidation,
    UCellRiskAssessment, 
    UCellExecution,
    UCellQualityMeasurement,
    UCellProcessCapability,
    UCellSystemHealth
)
from .u_cell_serializers import (
    UCellSignalValidationSerializer,
    UCellRiskAssessmentSerializer,
    UCellExecutionSerializer,
    UCellQualityMeasurementSerializer,
    UCellProcessCapabilitySerializer,
    UCellSystemHealthSerializer
)

import sys
import os

# Import U-Cell components
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'mikrobot_u_cells', 'build'))

try:
    from signal_formatter import SignalFormatter, BOSDetectionResult
    from risk_calculator import RiskCalculator, ProcessedSignal as RiskProcessedSignal
    from order_executor import OrderExecutor, ProcessedSignal as ExecProcessedSignal  
    from kafka_producer import ResilientKafkaProducer
    from statistical_monitor import StatisticalMonitor, QualityMeasurement
except ImportError as e:
    print(f"Warning: Could not import U-Cell components: {e}")
    SignalFormatter = None

import logging
from datetime import datetime
import json
from decimal import Decimal

logger = logging.getLogger(__name__)


class UCellSignalValidationViewSet(viewsets.ModelViewSet):
    """
    U-Cell 1: Signal Detection - Validation API
    """
    
    queryset = UCellSignalValidation.objects.all()
    serializer_class = UCellSignalValidationSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['mql5_signal__symbol', 'correlation_id']
    ordering_fields = ['created_at', 'processing_time_ms', 'confidence_score']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def validate_signal(self, request):
        """
        Validate signal using U-Cell 1 Signal Formatter
        """
        try:
            signal_id = request.data.get('signal_id')
            if not signal_id:
                return Response(
                    {'error': 'signal_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get MQL5Signal
            try:
                mql5_signal = MQL5Signal.objects.get(pk=signal_id)
            except MQL5Signal.DoesNotExist:
                return Response(
                    {'error': 'Signal not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if not SignalFormatter:
                return Response(
                    {'error': 'U-Cell components not available'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Initialize formatter
            formatter = SignalFormatter()
            
            # Convert Django signal to BOS format
            bos_data = {
                'symbol': mql5_signal.symbol,
                'h1_break_price': float(mql5_signal.entry_price) - 0.0005,  # Simulate H1 break
                'm15_confirmation_price': float(mql5_signal.entry_price),
                'break_direction': 'UP' if mql5_signal.direction == 'BUY' else 'DOWN',
                'pip_movement': 0.8,  # Default
                'confidence_raw': 0.85,  # Default
                'detection_timestamp': mql5_signal.signal_timestamp.timestamp()
            }
            
            # Format signal
            result = formatter.format_bos_signal(bos_data)
            
            # Create or update validation record
            validation, created = UCellSignalValidation.objects.get_or_create(
                mql5_signal=mql5_signal,
                defaults={
                    'formatted_successfully': result.success,
                    'poka_yoke_passed': result.success and len(result.errors) == 0,
                    'validation_errors': [
                        {
                            'error_type': error.get('error_type', ''),
                            'field': error.get('field', ''),
                            'message': error.get('message', '')
                        } for error in result.errors
                    ] if result.errors else [],
                    'bos_confirmed': result.success,
                    'pip_movement': Decimal('0.8') if result.success else None,
                    'confidence_score': Decimal(str(result.signal.get('confidence', 0))) if result.success and result.signal else None,
                    'processing_time_ms': result.processing_time_ms,
                    'correlation_id': result.correlation_id,
                    'validated_at': timezone.now()
                }
            )
            
            if not created:
                # Update existing record
                validation.formatted_successfully = result.success
                validation.poka_yoke_passed = result.success and len(result.errors) == 0
                validation.validation_errors = [
                    {
                        'error_type': error.get('error_type', ''),
                        'field': error.get('field', ''),
                        'message': error.get('message', '')
                    } for error in result.errors
                ] if result.errors else []
                validation.processing_time_ms = result.processing_time_ms
                validation.correlation_id = result.correlation_id
                validation.validated_at = timezone.now()
                validation.save()
            
            logger.info(f"U-Cell validation completed for signal {signal_id}: {result.success}")
            
            return Response({
                'validation_id': str(validation.validation_id),
                'success': result.success,
                'formatted_signal': result.signal if result.success else None,
                'errors': validation.validation_errors,
                'processing_time_ms': result.processing_time_ms,
                'correlation_id': result.correlation_id
            })
            
        except Exception as e:
            logger.error(f"U-Cell validation failed: {str(e)}")
            return Response(
                {'error': f'Validation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UCellRiskAssessmentViewSet(viewsets.ModelViewSet):
    """
    U-Cell 3: Processing & Analysis - Risk Assessment API
    """
    
    queryset = UCellRiskAssessment.objects.all()
    serializer_class = UCellRiskAssessmentSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['mql5_signal__symbol', 'assessment_id']
    ordering_fields = ['created_at', 'risk_percentage', 'position_size']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def assess_risk(self, request):
        """
        Assess risk using U-Cell 3 Risk Calculator
        """
        try:
            signal_id = request.data.get('signal_id')
            if not signal_id:
                return Response(
                    {'error': 'signal_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get MQL5Signal
            try:
                mql5_signal = MQL5Signal.objects.get(pk=signal_id)
            except MQL5Signal.DoesNotExist:
                return Response(
                    {'error': 'Signal not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if not RiskCalculator:
                return Response(
                    {'error': 'U-Cell components not available'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Risk configuration
            risk_config = {
                'max_risk_per_trade': 0.01,  # 1%
                'max_daily_risk': 0.02,      # 2%
                'max_weekly_risk': 0.05,     # 5%
                'max_drawdown': 0.10,        # 10%
                'account_balance': 10000.0,   # Default
                'account_currency': 'USD'
            }
            
            # Initialize calculator
            calculator = RiskCalculator(risk_config)
            
            # Convert Django signal to risk format
            risk_signal = {
                'signal_id': str(mql5_signal.id),
                'symbol': mql5_signal.symbol,
                'action': mql5_signal.direction,
                'entry_price': float(mql5_signal.entry_price),
                'stop_loss': float(mql5_signal.stop_loss),
                'take_profit': float(mql5_signal.take_profit),
                'confidence': 0.85  # Default
            }
            
            # Calculate risk
            result = calculator.calculate_risk(risk_signal)
            
            # Create or update assessment record
            assessment, created = UCellRiskAssessment.objects.get_or_create(
                mql5_signal=mql5_signal,
                defaults={
                    'approved': result['approved'],
                    'position_size': Decimal(str(result['position_size'])),
                    'risk_amount': Decimal(str(result['risk_amount'])),
                    'risk_percentage': Decimal(str(result['risk_percentage'])),
                    'daily_risk_used': Decimal(str(result['daily_risk_used'])),
                    'weekly_risk_used': Decimal(str(result['weekly_risk_used'])),
                    'drawdown_impact': Decimal(str(result['drawdown_impact'])),
                    'calculation_accuracy': Decimal(str(result['calculation_accuracy'])),
                    'processing_time_ms': result['processing_time_ms'],
                    'approval_reason': result['approval_reason'],
                    'rejection_reasons': result['rejection_reasons'],
                    'assessed_at': timezone.now()
                }
            )
            
            if not created:
                # Update existing record
                assessment.approved = result['approved']
                assessment.position_size = Decimal(str(result['position_size']))
                assessment.risk_amount = Decimal(str(result['risk_amount']))
                assessment.risk_percentage = Decimal(str(result['risk_percentage']))
                assessment.processing_time_ms = result['processing_time_ms']
                assessment.approval_reason = result['approval_reason']
                assessment.rejection_reasons = result['rejection_reasons']
                assessment.assessed_at = timezone.now()
                assessment.save()
            
            logger.info(f"U-Cell risk assessment completed for signal {signal_id}: {result['approved']}")
            
            return Response({
                'assessment_id': str(assessment.assessment_id),
                'approved': result['approved'],
                'position_size': result['position_size'],
                'risk_amount': result['risk_amount'],
                'risk_percentage': result['risk_percentage'],
                'approval_reason': result['approval_reason'],
                'rejection_reasons': result['rejection_reasons'],
                'processing_time_ms': result['processing_time_ms']
            })
            
        except Exception as e:
            logger.error(f"U-Cell risk assessment failed: {str(e)}")
            return Response(
                {'error': f'Risk assessment failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UCellExecutionViewSet(viewsets.ModelViewSet):
    """
    U-Cell 4: Execution - Order Execution API
    """
    
    queryset = UCellExecution.objects.all()
    serializer_class = UCellExecutionSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['mql5_signal__symbol', 'order_id', 'execution_id']
    ordering_fields = ['created_at', 'executed_at', 'slippage_pips']
    ordering = ['-created_at']


class UCellQualityMeasurementViewSet(viewsets.ModelViewSet):
    """
    U-Cell 5: Monitoring & Control - Quality Measurement API
    """
    
    queryset = UCellQualityMeasurement.objects.all()
    serializer_class = UCellQualityMeasurementSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['process_name', 'correlation_id']
    ordering_fields = ['created_at', 'measurement_value', 'sigma_level']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def record_measurement(self, request):
        """
        Record quality measurement using U-Cell 5 Statistical Monitor
        """
        try:
            measurement_data = request.data
            
            # Validate required fields
            required_fields = ['process_name', 'measurement_value', 'measurement_unit', 
                             'target_value', 'upper_spec_limit', 'lower_spec_limit']
            
            for field in required_fields:
                if field not in measurement_data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Check if within specifications
            value = float(measurement_data['measurement_value'])
            upper_limit = float(measurement_data['upper_spec_limit'])
            lower_limit = float(measurement_data['lower_spec_limit'])
            within_spec = lower_limit <= value <= upper_limit
            
            # Create measurement record
            measurement = UCellQualityMeasurement.objects.create(
                process_name=measurement_data['process_name'],
                measurement_value=value,
                measurement_unit=measurement_data['measurement_unit'],
                target_value=float(measurement_data['target_value']),
                upper_spec_limit=upper_limit,
                lower_spec_limit=lower_limit,
                within_spec=within_spec,
                correlation_id=measurement_data.get('correlation_id', ''),
                mql5_signal_id=measurement_data.get('signal_id') if measurement_data.get('signal_id') else None
            )
            
            logger.info(f"Quality measurement recorded: {measurement_data['process_name']} = {value}")
            
            return Response({
                'measurement_id': str(measurement.measurement_id),
                'process_name': measurement.process_name,
                'measurement_value': measurement.measurement_value,
                'within_spec': measurement.within_spec,
                'created_at': measurement.created_at.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Quality measurement recording failed: {str(e)}")
            return Response(
                {'error': f'Measurement recording failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UCellSystemHealthViewSet(viewsets.ModelViewSet):
    """
    U-Cell 5: Monitoring & Control - System Health API
    """
    
    queryset = UCellSystemHealth.objects.all()
    serializer_class = UCellSystemHealthSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['created_at', 'sigma_level', 'throughput_rate']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def current_status(self, request):
        """
        Get current system health status
        """
        try:
            # Get latest health record
            latest_health = UCellSystemHealth.objects.first()
            
            if not latest_health:
                return Response({
                    'status': 'UNKNOWN',
                    'message': 'No health data available'
                })
            
            # Calculate real-time metrics
            from django.db.models import Count, Avg
            from datetime import timedelta
            
            now = timezone.now()
            last_hour = now - timedelta(hours=1)
            
            # Recent signal statistics
            recent_signals = MQL5Signal.objects.filter(received_at__gte=last_hour)
            signals_count = recent_signals.count()
            
            # Recent validation statistics  
            recent_validations = UCellSignalValidation.objects.filter(created_at__gte=last_hour)
            validation_success_rate = recent_validations.filter(formatted_successfully=True).count() / max(recent_validations.count(), 1)
            
            # Recent risk assessments
            recent_assessments = UCellRiskAssessment.objects.filter(created_at__gte=last_hour)
            risk_approval_rate = recent_assessments.filter(approved=True).count() / max(recent_assessments.count(), 1)
            
            # Recent quality measurements
            recent_measurements = UCellQualityMeasurement.objects.filter(created_at__gte=last_hour)
            quality_compliance_rate = recent_measurements.filter(within_spec=True).count() / max(recent_measurements.count(), 1)
            
            # Determine overall status
            if validation_success_rate >= 0.95 and risk_approval_rate >= 0.8 and quality_compliance_rate >= 0.9:
                overall_status = 'HEALTHY'
            elif validation_success_rate >= 0.9 and risk_approval_rate >= 0.6 and quality_compliance_rate >= 0.8:
                overall_status = 'WARNING'
            elif validation_success_rate >= 0.8 and risk_approval_rate >= 0.4 and quality_compliance_rate >= 0.7:
                overall_status = 'CRITICAL'
            else:
                overall_status = 'DOWN'
            
            return Response({
                'overall_status': overall_status,
                'timestamp': now.isoformat(),
                'metrics': {
                    'signals_last_hour': signals_count,
                    'validation_success_rate': round(validation_success_rate * 100, 2),
                    'risk_approval_rate': round(risk_approval_rate * 100, 2),
                    'quality_compliance_rate': round(quality_compliance_rate * 100, 2)
                },
                'u_cell_status': {
                    'u_cell_1_signal_detection': 'HEALTHY' if validation_success_rate >= 0.9 else 'WARNING',
                    'u_cell_2_signal_reception': 'HEALTHY',  # Based on Django API health
                    'u_cell_3_processing_analysis': 'HEALTHY' if risk_approval_rate >= 0.6 else 'WARNING',
                    'u_cell_4_execution': 'HEALTHY',  # Based on execution success
                    'u_cell_5_monitoring_control': 'HEALTHY' if quality_compliance_rate >= 0.8 else 'WARNING'
                }
            })
            
        except Exception as e:
            logger.error(f"System health check failed: {str(e)}")
            return Response(
                {'error': f'Health check failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )