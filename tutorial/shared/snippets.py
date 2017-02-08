from flask import jsonify


def create_response(payload=None, message=None, status_code=200):
    """Create standard reply template.
        payload: A json-compatible parameter.
        status_code: HTTP return code. None implies 200, non-200 implies error.
        message: A message to the user.
    """
    was_success = status_code == 200
    meta = dict(was_success=was_success)
    if message:
        meta['message'] = message

    # This presumes a JSON reply; smarter code would be more flexible.
    response = jsonify(dict(
        payload=payload,
        meta=meta
        ))

    response.status_code = status_code
    return response


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def as_response(self):
        return create_response(self.payload, self.message, self.status_code)


class UndevelopedException(Exception):
    status_code = 400

    def __init__(self, message, status_code, payload=None):
        Exception.__init__(self)
        self.message = 'Development hole: %s' % (message,)
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def as_response(self):
        return create_response(self.payload, self.message, self.status_code)
