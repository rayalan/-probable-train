from flask import Blueprint, g, session

from .. import acl
from ..shared.snippets import create_response, InvalidUsage


game = Blueprint('game', __name__, url_prefix='/game')


@game.route('/wager/amount')
def on_wager_query():
    value = g.redis.get('wager_amount')
    return create_response(int(value or 0))


@game.route('/wager/amount/<amount>', methods=['POST'])
def on_wager(amount):
    value = g.redis.incrby('wager_amount', int(amount))
    if 'username' in session:
        g.redis.sadd('gamblers', session['username'])
    return create_response(int(value or 0))


@game.route('/outcome/<user>', methods=['POST'])
@acl.has_permission('admininstrator')
def on_rigged_outcome(user):
    if session['username']:
        g.redis.set('winner', user)
    return create_response({ 'winner' : user, 'state' : 'rigged' })


@game.route('/state/<mode>', methods=['POST'])
def on_game_state(mode):
    if mode == 'resolve':
        value = int(g.redis.get('wager_amount') or 0)
        winner = g.redis.get('winner') or g.redis.srandmember('gamblers')
        g.redis.delete('wager_amount', 'winner')
        return create_response({ 'winner' : winner, 'payout' : value })
    if mode == 'reset':
        g.redis.delete('wager_amount', 'gamblers')
        return create_response({ 'winner' : None, 'payout' : 0 })

    raise InvalidUsage('Unknown state for game: %s' % mode)

