"""
DoDD-Grade Rate Limiting System
Production-ready rate limiting for U-Cell endpoints (1000 req/h)
Created: 2025-07-23 - DoDD Phase Implementation
Status: READY FOR DEPLOYMENT (not active in development)
"""

import time
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

class DoddRateLimitMiddleware:
    """
    DoDD-Grade Rate Limiting Middleware
    Enforces 1000 requests per hour per user/IP
    Only active when settings.DEBUG = False
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_requests = getattr(settings, 'DODD_RATE_LIMIT_REQUESTS', 1000)
        self.rate_limit_window = getattr(settings, 'DODD_RATE_LIMIT_WINDOW', 3600)  # 1 hour
        
    def __call__(self, request):
        # Skip rate limiting in development mode
        if settings.DEBUG:
            return self.get_response(request)
        
        # Only apply to U-Cell API endpoints
        if not request.path.startswith('/api/v1/u-cell/'):
            return self.get_response(request)
        
        # Check rate limit
        if not self._check_rate_limit(request):
            return self._rate_limit_exceeded_response(request)
        
        response = self.get_response(request)
        
        # Add rate limit headers
        self._add_rate_limit_headers(response, request)
        
        return response
    
    def _check_rate_limit(self, request):
        """
        Check if request is within rate limit
        """
        identifier = self._get_rate_limit_identifier(request)
        cache_key = f"rate_limit_{identifier}"
        
        current_time = int(time.time())
        window_start = current_time - self.rate_limit_window
        
        # Get existing requests in current window
        requests = cache.get(cache_key, [])
        
        # Filter requests within current window
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if limit exceeded
        if len(requests) >= self.rate_limit_requests:
            self._log_rate_limit_exceeded(request, identifier, len(requests))
            return False
        
        # Add current request
        requests.append(current_time)
        cache.set(cache_key, requests, self.rate_limit_window)
        
        self._log_rate_limit_check(request, identifier, len(requests))
        return True
    
    def _get_rate_limit_identifier(self, request):
        """
        Get identifier for rate limiting (user ID or IP)
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user_{request.user.id}"
        else:
            return f"ip_{self._get_client_ip(request)}"
    
    def _get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _rate_limit_exceeded_response(self, request):
        """
        Return rate limit exceeded response
        """
        return JsonResponse(
            {
                'error': 'Rate limit exceeded',
                'detail': f'Maximum {self.rate_limit_requests} requests per hour allowed',
                'retry_after': self.rate_limit_window
            },
            status=429
        )
    
    def _add_rate_limit_headers(self, response, request):
        """
        Add rate limit headers to response
        """
        identifier = self._get_rate_limit_identifier(request)
        cache_key = f"rate_limit_{identifier}"
        
        requests = cache.get(cache_key, [])
        remaining = max(0, self.rate_limit_requests - len(requests))
        
        response['X-RateLimit-Limit'] = str(self.rate_limit_requests)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(int(time.time()) + self.rate_limit_window)
    
    def _log_rate_limit_check(self, request, identifier, current_count):
        """
        Log rate limit check for monitoring
        """
        logger.debug(
            f"Rate limit check - {identifier} - "
            f"Count: {current_count}/{self.rate_limit_requests} - "
            f"Path: {request.path}"
        )
    
    def _log_rate_limit_exceeded(self, request, identifier, current_count):
        """
        Log rate limit exceeded for audit
        """
        logger.warning(
            f"Rate limit EXCEEDED - {identifier} - "
            f"Count: {current_count}/{self.rate_limit_requests} - "
            f"Path: {request.path} - "
            f"IP: {self._get_client_ip(request)}"
        )


class DoddRateLimitDecorator:
    """
    Rate limiting decorator for specific views
    """
    
    def __init__(self, requests_per_hour=1000):
        self.requests_per_hour = requests_per_hour
        self.window = 3600  # 1 hour
    
    def __call__(self, view_func):
        def wrapper(request, *args, **kwargs):
            # Skip in development
            if settings.DEBUG:
                return view_func(request, *args, **kwargs)
            
            if not self._check_rate_limit(request):
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded for this endpoint',
                        'detail': f'Maximum {self.requests_per_hour} requests per hour'
                    },
                    status=429
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    def _check_rate_limit(self, request):
        """
        Check rate limit for specific view
        """
        identifier = self._get_identifier(request)
        view_name = request.resolver_match.view_name if request.resolver_match else 'unknown'
        cache_key = f"view_rate_limit_{identifier}_{view_name}"
        
        current_time = int(time.time())
        window_start = current_time - self.window
        
        requests = cache.get(cache_key, [])
        requests = [req_time for req_time in requests if req_time > window_start]
        
        if len(requests) >= self.requests_per_hour:
            return False
        
        requests.append(current_time)
        cache.set(cache_key, requests, self.window)
        return True
    
    def _get_identifier(self, request):
        """
        Get identifier for rate limiting
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user_{request.user.id}"
        else:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return f"ip_{ip}"


# Rate limiting configuration
DODD_RATE_LIMITS = {
    'default': 1000,  # requests per hour
    'u_cell_validations': 500,
    'u_cell_risk_assessments': 300,
    'u_cell_executions': 100,
    'u_cell_quality_measurements': 200,
    'u_cell_system_health': 1000
}