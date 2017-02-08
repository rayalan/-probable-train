from flask import Blueprint

from .. import acl
from ..shared import snippets


authentication = Blueprint('authentication', __name__, url_prefix='/auth')


@authentication.route('/login')
@acl.has_permission('user')
def on_login():
    return snippets.create_response()
