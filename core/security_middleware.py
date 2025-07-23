"""
DoDD-Grade Security Middleware
HTTPS enforcement, certificate validation, and security headers
Created: 2025-07-23 - DoDD Phase Implementation
Status: READY FOR DEPLOYMENT (not active in development)
"""

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.utils.deprecation import MiddlewareMixin
import logging
import ssl
import socket

logger = logging.getLogger(__name__)

class DoddSecurityMiddleware(MiddlewareMixin):
    """
    DoDD-Grade Security Middleware
    Enforces HTTPS, validates certificates, adds security headers
    Only active when settings.DEBUG = False
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response
        
    def process_request(self, request):
        """
        Process incoming request for security validation
        """
        # Skip security enforcement in development
        if settings.DEBUG:
            return None
        
        # Enforce HTTPS for U-Cell endpoints
        if request.path.startswith('/api/v1/u-cell/'):
            if not request.is_secure():
                return self._redirect_to_https(request)
        
        # Validate client certificate if required
        if getattr(settings, 'DODD_REQUIRE_CLIENT_CERT', False):
            if not self._validate_client_certificate(request):
                return self._client_cert_required_response()
        
        return None
    
    def process_response(self, request, response):
        """
        Add security headers to response
        """
        # Skip in development
        if settings.DEBUG:
            return response
        
        # Add DoDD security headers
        self._add_security_headers(response)
        
        # Log security events
        self._log_security_event(request, response)
        
        return response
    
    def _redirect_to_https(self, request):
        """
        Redirect HTTP requests to HTTPS
        """
        https_url = f"https://{request.get_host()}{request.get_full_path()}"
        
        logger.warning(
            f"HTTP request redirected to HTTPS - "
            f"IP: {self._get_client_ip(request)} - "
            f"Path: {request.path}"
        )
        
        return HttpResponsePermanentRedirect(https_url)
    
    def _validate_client_certificate(self, request):
        """
        Validate client SSL certificate
        """
        try:
            # Check for client certificate in headers (from reverse proxy)
            client_cert = request.META.get('HTTP_X_CLIENT_CERT')
            client_verify = request.META.get('HTTP_X_CLIENT_VERIFY')
            
            if not client_cert or client_verify != 'SUCCESS':
                logger.warning(
                    f"Client certificate validation failed - "
                    f"IP: {self._get_client_ip(request)} - "
                    f"Verify: {client_verify}"
                )
                return False
            
            logger.info(f"Client certificate validated - IP: {self._get_client_ip(request)}")
            return True
            
        except Exception as e:
            logger.error(f"Client certificate validation error: {e}")
            return False
    
    def _client_cert_required_response(self):
        """
        Return client certificate required response
        """
        return JsonResponse(
            {
                'error': 'Client certificate required',
                'detail': 'Valid client certificate must be provided for DoDD endpoints'
            },
            status=403
        )
    
    def _add_security_headers(self, response):
        """
        Add DoDD-required security headers
        """
        # Strict Transport Security
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'payment=(), '
            'usb=()'
        )
        
        # DoDD Custom Headers
        response['X-DoDD-API-Version'] = '1.0'
        response['X-FoxBox-Framework'] = 'DoDD-Hardened'
    
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
    
    def _log_security_event(self, request, response):
        """
        Log security events for audit trail
        """
        if request.path.startswith('/api/v1/u-cell/'):
            logger.info(
                f"DoDD Security - "
                f"Path: {request.path} - "
                f"Method: {request.method} - "
                f"Status: {response.status_code} - "
                f"IP: {self._get_client_ip(request)} - "
                f"HTTPS: {request.is_secure()} - "
                f"UA: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:50]}"
            )


class DoddSSLValidator:
    """
    SSL Certificate validation utilities
    """
    
    @staticmethod
    def validate_certificate(hostname, port=443):
        """
        Validate SSL certificate for hostname
        """
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    logger.info(f"SSL certificate validated for {hostname}")
                    return {
                        'valid': True,
                        'subject': cert.get('subject'),
                        'issuer': cert.get('issuer'),
                        'version': cert.get('version'),
                        'serial_number': cert.get('serialNumber'),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter')
                    }
                    
        except ssl.SSLError as e:
            logger.error(f"SSL validation failed for {hostname}: {e}")
            return {'valid': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Certificate validation error for {hostname}: {e}")
            return {'valid': False, 'error': str(e)}
    
    @staticmethod
    def get_certificate_info(request):
        """
        Extract certificate information from request
        """
        return {
            'client_cert': request.META.get('HTTP_X_CLIENT_CERT'),
            'client_cert_verify': request.META.get('HTTP_X_CLIENT_VERIFY'),
            'client_cert_subject': request.META.get('HTTP_X_CLIENT_CERT_SUBJECT'),
            'client_cert_issuer': request.META.get('HTTP_X_CLIENT_CERT_ISSUER'),
            'ssl_cipher': request.META.get('HTTP_X_SSL_CIPHER'),
            'ssl_protocol': request.META.get('HTTP_X_SSL_PROTOCOL')
        }