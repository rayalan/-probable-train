class BaseConfig(object):
    DEBUG = False
    LOG_LEVEL ='INFO'
    REDIS_HOST = 'localhost'
    VERSION = '0.0.1'

    # Test related variables
    TESTING = False
    IS_AUTHORIZATION_ENABLED = True
    REDIS_CONNECTION = None


class DefaultConfig(BaseConfig):
    DEBUG = True
    SECRET_KEY = 'TutorialsAreAwesome'  # Required string for securing session cookies.
    REDIS_PORT = 6380


class TestingConfig(BaseConfig):
    IS_AUTHORIZATION_ENABLED = False
    DEBUG = True
    REDIS_PORT = 6379
    TESTING = True


try:
    import local
except ImportError:
    # Flask considers modules and objects to be roughly equivalent, so this means no local overrides
    local = {}
