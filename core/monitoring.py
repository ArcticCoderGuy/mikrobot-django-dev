"""
DoDD-Grade Monitoring and Audit Trail System
Comprehensive logging, monitoring, and dashboard functionality
Created: 2025-07-23 - DoDD Phase Implementation
Status: READY FOR DEPLOYMENT
"""

import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import threading

logger = logging.getLogger(__name__)

class DoddAuditLog(models.Model):
    """
    DoDD Audit Log Model for tracking all U-Cell operations
    """
    
    EVENT_TYPES = [
        ('API_REQUEST', 'API Request'),
        ('AUTHENTICATION', 'Authentication'),
        ('AUTHORIZATION', 'Authorization'),
        ('RATE_LIMIT', 'Rate Limit'),
        ('ERROR', 'Error'),
        ('SECURITY', 'Security Event'),
        ('DATA_ACCESS', 'Data Access'),
        ('SYSTEM', 'System Event')
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical')
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='LOW')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time_ms = models.IntegerField()
    user_agent = models.TextField()
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    correlation_id = models.UUIDField()
    
    class Meta:
        db_table = 'dodd_audit_log'
        indexes = [
            models.Index(fields=['timestamp', 'event_type']),
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.event_type} - {self.endpoint}"


class DoddSystemMetrics(models.Model):
    """
    System performance metrics for monitoring
    """
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    active_connections = models.IntegerField()
    api_requests_per_minute = models.IntegerField()
    error_rate = models.FloatField()
    avg_response_time = models.FloatField()
    
    class Meta:
        db_table = 'dodd_system_metrics'


class DoddMonitoringService:
    """
    DoDD Monitoring Service for real-time system monitoring
    """
    
    def __init__(self):
        self.metrics_cache_key = 'dodd_metrics'
        self.alert_cache_key = 'dodd_alerts'
        self.monitoring_active = not settings.DEBUG  # Only active in production
    
    def log_api_request(self, request, response, start_time):
        """
        Log API request for audit trail
        """
        if not self.monitoring_active:
            return
        
        try:
            end_time = time.time()
            response_time = int((end_time - start_time) * 1000)
            
            # Create audit log entry
            DoddAuditLog.objects.create(
                event_type='API_REQUEST',
                severity=self._get_severity_from_status(response.status_code),
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                ip_address=self._get_client_ip(request),
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                response_time_ms=response_time,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
                request_data=self._sanitize_request_data(request),
                response_data=self._sanitize_response_data(response),
                correlation_id=getattr(request, 'correlation_id', None)
            )
            
            # Update real-time metrics
            self._update_real_time_metrics(response_time, response.status_code)
            
        except Exception as e:
            logger.error(f"Failed to log API request: {e}")
    
    def log_security_event(self, event_type, severity, details, request=None):
        """
        Log security event
        """
        if not self.monitoring_active:
            return
        
        try:
            DoddAuditLog.objects.create(
                event_type='SECURITY',
                severity=severity,
                user=request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None,
                ip_address=self._get_client_ip(request) if request else '0.0.0.0',
                endpoint=request.path if request else 'system',
                method=request.method if request else 'SYSTEM',
                status_code=0,
                response_time_ms=0,
                user_agent=request.META.get('HTTP_USER_AGENT', '') if request else 'system',
                request_data={'event_type': event_type, 'details': details},
                response_data={},
                correlation_id=getattr(request, 'correlation_id', None) if request else None
            )
            
            # Trigger alert for high/critical severity
            if severity in ['HIGH', 'CRITICAL']:
                self._trigger_alert(f"Security Event: {event_type}", details, severity)
                
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    def collect_system_metrics(self):
        """
        Collect system performance metrics
        """
        if not self.monitoring_active:
            return
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get application metrics from cache
            api_metrics = cache.get('api_metrics', {})
            
            # Store metrics
            DoddSystemMetrics.objects.create(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                active_connections=self._get_active_connections(),
                api_requests_per_minute=api_metrics.get('requests_per_minute', 0),
                error_rate=api_metrics.get('error_rate', 0.0),
                avg_response_time=api_metrics.get('avg_response_time', 0.0)
            )
            
            # Check for alerts
            self._check_system_alerts(cpu_percent, memory.percent, disk.percent)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def get_dashboard_data(self):
        """
        Get dashboard data for monitoring interface
        """
        try:
            # Recent metrics (last 24 hours)
            recent_metrics = DoddSystemMetrics.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-timestamp')[:100]
            
            # Recent audit logs (last 1000 entries)
            recent_logs = DoddAuditLog.objects.select_related('user').order_by('-timestamp')[:1000]
            
            # Error rate by endpoint
            error_logs = DoddAuditLog.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=24),
                status_code__gte=400
            ).values('endpoint').annotate(
                error_count=models.Count('id')
            ).order_by('-error_count')[:10]
            
            # Top users by API usage
            top_users = DoddAuditLog.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=24),
                user__isnull=False
            ).values('user__username').annotate(
                request_count=models.Count('id')
            ).order_by('-request_count')[:10]
            
            return {
                'system_metrics': [
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'cpu_usage': m.cpu_usage,
                        'memory_usage': m.memory_usage,
                        'disk_usage': m.disk_usage,
                        'active_connections': m.active_connections,
                        'api_requests_per_minute': m.api_requests_per_minute,
                        'error_rate': m.error_rate,
                        'avg_response_time': m.avg_response_time
                    } for m in recent_metrics
                ],
                'audit_logs': [
                    {
                        'timestamp': log.timestamp.isoformat(),
                        'event_type': log.event_type,
                        'severity': log.severity,
                        'user': log.user.username if log.user else 'Anonymous',
                        'ip_address': log.ip_address,
                        'endpoint': log.endpoint,
                        'method': log.method,
                        'status_code': log.status_code,
                        'response_time_ms': log.response_time_ms
                    } for log in recent_logs
                ],
                'error_summary': [
                    {
                        'endpoint': error['endpoint'],
                        'error_count': error['error_count']
                    } for error in error_logs
                ],
                'top_users': [
                    {
                        'username': user['user__username'],
                        'request_count': user['request_count']
                    } for user in top_users
                ],
                'alerts': cache.get(self.alert_cache_key, [])
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {}
    
    def _get_severity_from_status(self, status_code):
        """
        Get severity level from HTTP status code
        """
        if status_code >= 500:
            return 'CRITICAL'
        elif status_code >= 400:
            return 'HIGH'
        elif status_code >= 300:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
    
    def _sanitize_request_data(self, request):
        """
        Sanitize request data for logging (remove sensitive info)
        """
        sensitive_fields = ['password', 'token', 'api_key', 'secret', 'auth']
        data = {}
        
        try:
            if hasattr(request, 'data'):
                data = dict(request.data)
            elif request.method == 'POST' and hasattr(request, 'POST'):
                data = dict(request.POST)
            
            # Remove sensitive fields
            for field in sensitive_fields:
                if field in data:
                    data[field] = '[REDACTED]'
            
            return data
        except:
            return {}
    
    def _sanitize_response_data(self, response):
        """
        Sanitize response data for logging
        """
        try:
            if hasattr(response, 'data') and len(str(response.data)) < 1000:
                return response.data
            else:
                return {'status': 'logged', 'size': len(str(response.content)) if hasattr(response, 'content') else 0}
        except:
            return {}
    
    def _update_real_time_metrics(self, response_time, status_code):
        """
        Update real-time metrics cache
        """
        try:
            current_metrics = cache.get('api_metrics', {
                'total_requests': 0,
                'total_errors': 0,
                'total_response_time': 0,
                'requests_this_minute': 0,
                'minute_timestamp': int(time.time() // 60)
            })
            
            current_minute = int(time.time() // 60)
            
            # Reset minute counter if new minute
            if current_metrics['minute_timestamp'] != current_minute:
                current_metrics['requests_this_minute'] = 0
                current_metrics['minute_timestamp'] = current_minute
            
            # Update metrics
            current_metrics['total_requests'] += 1
            current_metrics['requests_this_minute'] += 1
            current_metrics['total_response_time'] += response_time
            
            if status_code >= 400:
                current_metrics['total_errors'] += 1
            
            # Calculate rates
            current_metrics['requests_per_minute'] = current_metrics['requests_this_minute']
            current_metrics['error_rate'] = (current_metrics['total_errors'] / current_metrics['total_requests']) * 100
            current_metrics['avg_response_time'] = current_metrics['total_response_time'] / current_metrics['total_requests']
            
            cache.set('api_metrics', current_metrics, 3600)  # 1 hour
            
        except Exception as e:
            logger.error(f"Failed to update real-time metrics: {e}")
    
    def _get_active_connections(self):
        """
        Get number of active database connections
        """
        try:
            from django.db import connections
            return len(connections.all())
        except:
            return 0
    
    def _check_system_alerts(self, cpu_percent, memory_percent, disk_percent):
        """
        Check for system alerts
        """
        alerts = []
        
        if cpu_percent > 80:
            alerts.append({
                'type': 'CPU_HIGH',
                'severity': 'HIGH' if cpu_percent > 90 else 'MEDIUM',
                'message': f'CPU usage high: {cpu_percent:.1f}%',
                'timestamp': timezone.now().isoformat()
            })
        
        if memory_percent > 80:
            alerts.append({
                'type': 'MEMORY_HIGH',
                'severity': 'HIGH' if memory_percent > 90 else 'MEDIUM',
                'message': f'Memory usage high: {memory_percent:.1f}%',
                'timestamp': timezone.now().isoformat()
            })
        
        if disk_percent > 80:
            alerts.append({
                'type': 'DISK_HIGH',
                'severity': 'HIGH' if disk_percent > 90 else 'MEDIUM',
                'message': f'Disk usage high: {disk_percent:.1f}%',
                'timestamp': timezone.now().isoformat()
            })
        
        if alerts:
            # Store alerts in cache
            existing_alerts = cache.get(self.alert_cache_key, [])
            existing_alerts.extend(alerts)
            
            # Keep only recent alerts (last 100)
            existing_alerts = existing_alerts[-100:]
            cache.set(self.alert_cache_key, existing_alerts, 3600)
    
    def _trigger_alert(self, title, details, severity):
        """
        Trigger alert notification
        """
        alert = {
            'title': title,
            'details': details,
            'severity': severity,
            'timestamp': timezone.now().isoformat()
        }
        
        # Store in cache
        alerts = cache.get(self.alert_cache_key, [])
        alerts.append(alert)
        alerts = alerts[-100:]  # Keep last 100 alerts
        cache.set(self.alert_cache_key, alerts, 3600)
        
        # Log critical alerts
        if severity == 'CRITICAL':
            logger.critical(f"DODD ALERT: {title} - {details}")


# Global monitoring service instance
monitoring_service = DoddMonitoringService()


class DoddMonitoringMiddleware:
    """
    Middleware for automatic monitoring and logging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip monitoring in development
        if settings.DEBUG:
            return self.get_response(request)
        
        # Only monitor U-Cell endpoints
        if not request.path.startswith('/api/v1/u-cell/'):
            return self.get_response(request)
        
        start_time = time.time()
        
        # Add correlation ID
        import uuid
        request.correlation_id = uuid.uuid4()
        
        response = self.get_response(request)
        
        # Log the request
        monitoring_service.log_api_request(request, response, start_time)
        
        return response