import bottle
import base64
import random


AUTH_KEY = None


def _make_key(l=16):
    global AUTH_KEY
    s = hex(random.getrandbits(8 * l))[2:]
    if s[-1] == 'L':
        s = s[:-1]
    # Pad with zeros
    if len(s) != l * 2:
        s = '0' * (2 * l - len(s)) + s
    AUTH_KEY = base64.urlsafe_b64encode(s.decode('hex')).rstrip('=')
    print('AUTH_KEY: /?auth=%s' % AUTH_KEY)


def verify(enabled):

    def inner(func):

        def inner2(*args, **kw):
            if not enabled():
                return func(*args, **kw)
            try:
                auth = bottle.request.query['auth']
            except KeyError:
                bottle.abort(401)
            else:
                if auth != AUTH_KEY:
                    bottle.abort(401)
            return func(*args, **kw)
        if AUTH_KEY is None:
            _make_key()
        return inner2
    return inner
