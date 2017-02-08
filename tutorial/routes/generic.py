from flask import Blueprint, current_app, Response, jsonify

frontend = Blueprint('frontend', __name__, url_prefix='')


@frontend.route('/routes.<ext>')
def routes(ext):
    import urllib

    output = []
    for rule in current_app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        output.append((rule.endpoint, methods, urllib.unquote(str(rule))))

    output = sorted(output)
    if ext == "json":
        return jsonify({"routes" : output})

    output = ['{0:50s} {1:20s} {2}'.format(rule_endpoint, methods, rule) for rule_endpoint, methods, rule in output]
    output = '\n'.join(output) + '\n'
    return Response(output, mimetype='text/plain')
