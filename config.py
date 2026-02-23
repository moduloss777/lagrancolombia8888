"""
Configuración centralizada
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base"""
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sms_marketing.db')
    
    # TraffiLink
    TRAFFILINK_ACCOUNT = os.environ.get('TRAFFILINK_ACCOUNT', '')
    TRAFFILINK_PASSWORD = os.environ.get('TRAFFILINK_PASSWORD', '')
    TRAFFILINK_URL = os.environ.get('TRAFFILINK_URL', 'http://47.236.91.242:20003')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Environment
    AMBIENTE = os.environ.get('AMBIENTE', 'desarrollo')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    
    # Port
    PORT = int(os.environ.get('PORT', 5000))

# Instancia global
config = Config()
