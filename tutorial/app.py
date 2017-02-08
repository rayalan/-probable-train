import logging
import redis

from flask import Flask, g

from settings.config import DefaultConfig
from settings.config import local as localconfig  # Rename for clarity

from shared import snippets

from routes.authentication import authentication
from routes.game import game
from routes.generic import frontend
from acl import PermissionManager


class GenericApp(Flask):
    def __init__(self, *args, **kwargs):
        Flask.__init__(self, *args, **kwargs)

    def get_send_file_max_age(self, name):
        # Static files normally don't change during production, but during development, caching is curse.
        return 0 if self.debug else Flask.get_send_file_max_age(self, name)


class TutorialApp(GenericApp):
    BLUEPRINTS = (game, authentication, frontend)


def create_app(config=None):
    import_name = __name__
    app = TutorialApp(import_name=import_name)

    configure_app(app, config, permission_manager=PermissionManager())
    configure_hook(app)
    configure_blueprints(app, app.BLUEPRINTS)
    configure_logging(app)
    configure_error_handlers(app)
    return app


def configure_app(app, config, permission_manager=None):
    app.config.from_object(DefaultConfig)
    app.config.from_object(localconfig)
    if config is not None:
        app.config.from_object(config)
    app.config.from_envvar('TUTORIAL_APP_CONFIG', silent=True)  # Override setting by env var without touching codes.

    app.config['redis'] = app.config['REDIS_CONNECTION'] or redis.StrictRedis(host=app.config['REDIS_HOST'],
                                                                              port=app.config['REDIS_PORT'])
    app.config['permission_manager'] = permission_manager


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_hook(app):
    @app.before_request
    def before_request():
        g.redis = app.config['redis']

    @app.after_request
    def control_cache(response):
        response.cache_control.no_cache = True
        if response.mimetype == 'application/json':
            response.cache_control.no_store = True
        return response


def configure_logging(app):
    message_format = "%(levelname)s:%(name)s:%(funcName)s:%(lineno)s:%(message)s"
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    logging.basicConfig(level=log_level, format=message_format)

    if app.config['TESTING']:
        return

    app.logger.setLevel(log_level)


def configure_error_handlers(app):
    @app.errorhandler(snippets.InvalidUsage)
    def handle_invalid_usage(error):
        return error.as_response()

    @app.errorhandler(snippets.UndevelopedException)
    def handle_undeveloped_exception(error):
        app.logger.exception('Undeveloped code: %s', error.message)
        return error.as_response()

    def handle_invalid_db_operation(error):
        app.logger.exception('Exception reached flask error handler...')
        return snippets.create_response(message=str(error), status_code=400)
