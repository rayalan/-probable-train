from base64 import b64encode
import json
import unittest

import redis

from ..settings.config import TestingConfig
from ..app import create_app


app = create_app(TestingConfig)
auth_app = create_app(TestingConfig)
auth_app.config['IS_AUTHORIZATION_ENABLED'] = True

DEFAULT_WAGER_AMOUNT = 23


def create_auth_header(username, password):
    return { 'Authorization': 'Basic ' + b64encode("{0}:{1}".format(username, password)) }


class GameTest(unittest.TestCase):
    def setUp(self):
        self.redis = redis.StrictRedis(port=6379)
        self.redis.set('wager_amount', DEFAULT_WAGER_AMOUNT)
        self.app = app.test_client()

    def test_home(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 404)

    def test_read_wager_amount(self):
        rv = self.app.get('/game/wager/amount')
        data = json.loads(rv.data)
        self.assertEqual(data.get('payload'), DEFAULT_WAGER_AMOUNT)

    def test_write_wager_amount(self):
        wager_amount = 52  # String because we're lazy
        rv = self.app.post('/game/wager/amount/' + str(wager_amount))
        data = json.loads(rv.data)
        self.assertEqual(data.get('payload'), wager_amount + DEFAULT_WAGER_AMOUNT)


class CanAuthorizeTest(unittest.TestCase):
    def setUp(self):
        self.app = auth_app.test_client()

    def test_login_bad(self):
        rv = self.app.get('/auth/login')
        self.assertEqual(rv.status_code, 400)

    def test_unauthorized_rigging(self):
        rv = self.app.post('/game/outcome/fred')
        self.assertEqual(rv.status_code, 400)


class WhileAuthorizedTest(unittest.TestCase):
    def setUp(self):
        self.redis = redis.StrictRedis(port=6379)
        self.redis.delete('winner')
        self.app = auth_app.test_client()
        headers = create_auth_header('alan.ray', 'bob')  # Best security practice ever!
        self._rv = self.app.get('/auth/login', headers=headers)

    def test_login_success(self):
        self.assertEqual(self._rv.status_code, 200)
        self.assertTrue('Set-Cookie' in self._rv.headers)

    def test_rig_winner(self):
        rv = self.app.post('/game/outcome/charlie')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(self.redis.get('winner'), 'charlie')


if __name__ == '__main__':
    unittest.main()
