from decouple import config, AutoString
import os

ENV = config('TEST_ENV', default='dev')

class TestConfig:
    BASE_URL = config('TEST_BASE_URL', default='http://127.0.0.1:8000')
    API_BASE_URL = config('TEST_API_BASE_URL', default='http://127.0.0.1:8000/api')
    
    BROWSER = config('TEST_BROWSER', default='chromium')
    HEADLESS = config('TEST_HEADLESS', default='true', cast=bool)
    SLOWMO = config('TEST_SLOWMO', default=0, cast=int)
    
    DB_NAME = config('DATABASE_NAME', default='test_olive_erp')
    DB_USER = config('DATABASE_USER', default='root')
    DB_PASSWORD = config('DATABASE_PASSWORD', default='')
    DB_HOST = config('DATABASE_HOST', default='localhost')
    DB_PORT = config('DATABASE_PORT', default='3306')
    
    ADMIN_USERNAME = config('TEST_ADMIN_USERNAME', default='testadmin')
    ADMIN_PASSWORD = config('TEST_ADMIN_PASSWORD', default='testpass123')
    ADMIN_EMAIL = config('TEST_ADMIN_EMAIL', default='admin@testcompany.com')
    
    USER_USERNAME = config('TEST_USER_USERNAME', default='employee_user')
    USER_PASSWORD = config('TEST_USER_PASSWORD', default='testpass123')
    USER_EMAIL = config('TEST_USER_EMAIL', default='employee@testcompany.com')
    
    TIMEOUT = config('TEST_TIMEOUT', default=30000, cast=int)
    SCREENSHOT_ON_FAILURE = config('TEST_SCREENSHOT_ON_FAILURE', default='true', cast=bool)
    VIDEO_ON_FAILURE = config('TEST_VIDEO_ON_FAILURE', default='false', cast=bool)
    
    LOG_LEVEL = config('TEST_LOG_LEVEL', default='INFO')
    
    @classmethod
    def is_dev(cls):
        return ENV == 'dev'
    
    @classmethod
    def is_staging(cls):
        return ENV == 'staging'
    
    @classmethod
    def is_prod(cls):
        return ENV == 'prod'
    
    @classmethod
    def is_ci(cls):
        return os.getenv('CI', 'false').lower() == 'true'

def get_config():
    return TestConfig

settings = TestConfig()
