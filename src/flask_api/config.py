# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
"""
Flask API Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('FLASK_PORT', 5000))

    # Generated clients directory
    GENERATED_CLIENTS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'generated_clients'
    )

    # Platform credentials (for production mode)
    PLATFORM_TOKENS = {
        'snapchat': os.getenv('SNAPCHAT_ACCESS_TOKEN'),
        'pinterest': os.getenv('PINTEREST_ACCESS_TOKEN'),
        'facebook': os.getenv('FACEBOOK_ACCESS_TOKEN'),
        'tiktok': os.getenv('TIKTOK_ACCESS_TOKEN'),
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
