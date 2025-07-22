"""
MikroBot MCP Production Settings
High-performance, fault-tolerant configuration for live trading
"""
import os
import json
import logging.config
from pathlib import Path
from .settings import *

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'mikrobot-production-key-change-this!')

# Production mode
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'mikrobot_production'),
        'USER': os.environ.get('DB_USER', 'mikrobot_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'MikroBot_2025_Secure!'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'prefer',
        },
        'CONN_MAX_AGE': 600,  # Connection pooling
        'CONN_HEALTH_CHECKS': True,
    }
}

# Cache - Redis for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}/1",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 100,
                'retry_on_timeout': True,
            }
        }
    }
}

# Session storage in Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap_servers': [os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')],
    'security_protocol': 'PLAINTEXT',
    'api_version': (2, 8, 1),
    'client_id': 'mikrobot-mcp',
    'group_id': 'mikrobot-mcp-group',
    'auto_offset_reset': 'latest',
    'enable_auto_commit': True,
    'auto_commit_interval_ms': 1000,
    'max_poll_records': 500,
    'max_poll_interval_ms': 300000,
    'session_timeout_ms': 30000,
    'heartbeat_interval_ms': 10000,
    'retry_backoff_ms': 100,
    'request_timeout_ms': 30000,
}

# Kafka Topics Configuration
KAFKA_TOPICS = {
    'PURE_SIGNALS': 'pure-signals',
    'PROCESSED_SIGNALS': 'processed-signals', 
    'TRADE_EXECUTIONS': 'trade-executions',
    'SYSTEM_EVENTS': 'system-events',
}

# MCP Agent Configuration
MCP_CONFIG = {
    'AGENT_NAME': 'mikrobot-mcp-agent',
    'PROCESSING_THREADS': 4,
    'HEARTBEAT_INTERVAL': 10,  # seconds
    'MAX_SIGNALS_PER_MINUTE': 100,
    'AUTO_RESTART_ENABLED': True,
    'FAILURE_THRESHOLD': 3,
    'RESTART_DELAY_SECONDS': 30,
}

# Structured JSON Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d'
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'trading': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(signal_id)s %(symbol)s %(direction)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'mikrobot_mcp.log',
            'maxBytes': 1024*1024*100,  # 100MB
            'backupCount': 10,
            'formatter': 'json',
            'level': 'INFO',
        },
        'trading_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'trading.log',
            'maxBytes': 1024*1024*50,   # 50MB
            'backupCount': 20,
            'formatter': 'trading',
            'level': 'INFO',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'maxBytes': 1024*1024*50,   # 50MB
            'backupCount': 5,
            'formatter': 'json',
            'level': 'ERROR',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'mikrobot.mcp': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'mikrobot.trading': {
            'handlers': ['console', 'trading_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'mikrobot.signals': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'kafka': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'WARNING',
    }
}

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Performance Settings
USE_TZ = True
USE_I18N = False  # Disable if not needed for performance
USE_L10N = False  # Disable if not needed for performance

# Database Connection Pooling
DATABASE_POOL_ARGS = {
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Email configuration (for alerts)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'mikrobot@example.com')

# Alert Configuration
ALERT_CONFIG = {
    'EMAIL_ALERTS': True,
    'SMS_ALERTS': False,  # Implement if needed
    'DISCORD_WEBHOOK_URL': os.environ.get('DISCORD_ALERT_WEBHOOK', ''),
    'ALERT_LEVELS': {
        'CRITICAL': ['email', 'discord'],
        'ERROR': ['email'],
        'WARNING': ['discord'],
        'INFO': [],
    }
}

# Create logs directory if it doesn't exist
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# MT5 Configuration (production)
MT5_CONFIG = {
    'login': int(os.environ.get('MT5_LOGIN', '107033449')),
    'password': os.environ.get('MT5_PASSWORD', 'P-Gt5uLw'),
    'server': os.environ.get('MT5_SERVER', 'Ava-Demo 1-MT5'),
    'timeout': 10000,
    'portable': False,
}

# Risk Management Configuration
RISK_CONFIG = {
    'MAX_RISK_PER_TRADE': 0.02,  # 2% per trade
    'MAX_DAILY_RISK': 0.06,      # 6% per day
    'MAX_OPEN_POSITIONS': 5,
    'MIN_RR_RATIO': 1.5,
    'MAX_DRAWDOWN_STOP': 0.15,   # 15% max drawdown
    'CORRELATION_LIMIT': 0.7,    # Max correlation between positions
}

# Feature Flags
FEATURE_FLAGS = {
    'ENABLE_ML_FILTERING': True,
    'ENABLE_REAL_TIME_ANALYSIS': True,
    'ENABLE_AUTO_EXECUTION': True,
    'ENABLE_POSITION_SIZING': True,
    'ENABLE_CORRELATION_FILTERING': True,
    'DEBUG_MODE': False,
}

# Monitoring and Health Checks
HEALTH_CHECK_CONFIG = {
    'KAFKA_HEALTH_CHECK': True,
    'POSTGRES_HEALTH_CHECK': True,
    'REDIS_HEALTH_CHECK': True,
    'MT5_HEALTH_CHECK': True,
    'HEALTH_CHECK_INTERVAL': 60,  # seconds
}