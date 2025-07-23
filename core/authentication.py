"""
DoDD-Grade Authentication System
Production-ready API Key + JWT authentication for U-Cell endpoints
Created: 2025-07-23 - DoDD Phase Implementation
"""

import jwt
import uuid
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authtoken.models import Token
from django.core.cache import cache
import logging
import hashlib

logger = logging.getLogger(__name__)

class DoddApiKeyAuthentication(authentication.BaseAuthentication):
    """
    DoDD-Grade API Key Authentication
    Supports both API Key and JWT token validation
    """
    
    def authenticate(self, request):
        """
        Authenticate API Key or JWT Token
        """
        api_key = request.META.get('HTTP_X_API_KEY')
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        # Try API Key authentication first
        if api_key:
            return self._authenticate_api_key(api_key, request)
        
        # Try JWT authentication
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            return self._authenticate_jwt_token(token, request)
        
        return None
    
    def _authenticate_api_key(self, api_key, request):
        """
        Validate API Key and return user
        """
        try:
            # Hash the API key for secure comparison
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Check cache first for performance
            cache_key = f"api_key_{api_key_hash}"
            user_id = cache.get(cache_key)
            
            if user_id:
                user = User.objects.get(id=user_id)
                self._log_authentication(request, user, 'API_KEY', 'SUCCESS')
                return (user, api_key)
            
            # Validate against stored API keys
            try:
                token = Token.objects.get(key=api_key)
                user = token.user
                
                # Cache for 5 minutes
                cache.set(cache_key, user.id, 300)
                
                self._log_authentication(request, user, 'API_KEY', 'SUCCESS')
                return (user, api_key)
                
            except Token.DoesNotExist:
                self._log_authentication(request, None, 'API_KEY', 'INVALID_TOKEN')
                raise exceptions.AuthenticationFailed('Invalid API key')
                
        except Exception as e:
            logger.error(f"API Key authentication error: {e}")
            self._log_authentication(request, None, 'API_KEY', 'ERROR')
            raise exceptions.AuthenticationFailed('Authentication failed')
    
    def _authenticate_jwt_token(self, token, request):
        """
        Validate JWT Token and return user
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=['HS256']
            )
            
            user_id = payload.get('user_id')
            exp = payload.get('exp')
            
            # Check token expiration
            if datetime.utcnow().timestamp() > exp:
                self._log_authentication(request, None, 'JWT', 'EXPIRED')
                raise exceptions.AuthenticationFailed('Token expired')
            
            # Get user
            user = User.objects.get(id=user_id)
            
            self._log_authentication(request, user, 'JWT', 'SUCCESS')
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            self._log_authentication(request, None, 'JWT', 'EXPIRED')
            raise exceptions.AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            self._log_authentication(request, None, 'JWT', 'INVALID')
            raise exceptions.AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            self._log_authentication(request, None, 'JWT', 'USER_NOT_FOUND')
            raise exceptions.AuthenticationFailed('User not found')
        except Exception as e:
            logger.error(f"JWT authentication error: {e}")
            self._log_authentication(request, None, 'JWT', 'ERROR')
            raise exceptions.AuthenticationFailed('Authentication failed')
    
    def _log_authentication(self, request, user, auth_type, status):
        """
        Log authentication attempts for audit trail
        """
        logger.info(
            f"DoDD Auth: {auth_type} - {status} - "
            f"User: {user.username if user else 'Unknown'} - "
            f"IP: {self._get_client_ip(request)} - "
            f"UA: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}"
        )
    
    def _get_client_ip(self, request):
        """
        Get client IP address for logging
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class JWTTokenGenerator:
    """
    JWT Token generation and management
    """
    
    @staticmethod
    def generate_token(user, expires_in_hours=24):
        """
        Generate JWT token for user
        """
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow(),
            'jti': str(uuid.uuid4())  # JWT ID for token revocation
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        logger.info(f"JWT token generated for user: {user.username}")
        return token
    
    @staticmethod
    def decode_token(token):
        """
        Decode and validate JWT token
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')


class DoddPermissionClass:
    """
    DoDD-specific permission validation
    """
    
    @staticmethod
    def has_u_cell_access(user):
        """
        Check if user has access to U-Cell endpoints
        """
        # Check user groups or permissions
        if user.is_superuser or user.groups.filter(name='u_cell_operators').exists():
            return True
        return False
    
    @staticmethod
    def get_rate_limit_key(user, view_name):
        """
        Generate rate limit key for user and view
        """
        return f"rate_limit_{user.id}_{view_name}"