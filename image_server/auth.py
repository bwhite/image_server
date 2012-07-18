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
    print('AUTH_KEY: /%s/' % AUTH_KEY)


def verify(func):

    def inner(*args, **kw):
        if not bottle.request.path.startswith('/%s/' % AUTH_KEY):
            bottle.abort(401)
        return func(*args, **kw)
    if AUTH_KEY is None:
        _make_key()
    return inner
