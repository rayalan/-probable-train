from functools import wraps

from flask import current_app, g, request, session

from shared.snippets import InvalidUsage

class PermissionManager(object):
    def __init__(self):
        self.administrators = ['alan.ray']
        self.users = ['alan.ray']


def is_authorized(permission, **kwargs):
    """Raises invalid usage response on failure"""
    # If we're ignoring authorization restrictions, automatically succeed immediately (and don't call the database,
    # which we don't want to be unnecessarily dependent on)
    if not current_app.config['IS_AUTHORIZATION_ENABLED']:
        return True

    current_role = session.get('role')
    if not current_role:  # Check for basic authentication. If it exists, try to login and update role
        request_authorization = request.authorization
        if request_authorization:
            login(request_authorization.username, request_authorization.password)
            current_role = session.get('role')

    return bool(current_role)


def has_permission(permission):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not is_authorized(permission, **kwargs):
                current_role = session.get('role')
                raise InvalidUsage('Authorization denied (%s)' % (current_role or 'No role',))
            return fn(*args, **kwargs)
        return wrapped
    return wrapper


def login(username, password):
    if password and username in current_app.config['permission_manager'].administrators:  # TODO: Maybe we shouldn't let any password be valid?
        session['user_id'] = username
        session['username'] = username
        session['role'] = 'admin'
        session['default_role'] = 'admin'
        session['available_roles'] = ['admin', 'user']
        return True

    logout()  # Wipe credentials in case previous valid login existed
    return False


def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('default_role', None)
    session.pop('available_roles', [])
