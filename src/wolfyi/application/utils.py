import re
from functools import wraps

from flask import current_app, escape, redirect, request


VALID_EMAIL_RE = re.compile(r'''^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$''')


def redirect_to_https(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if request.scheme != 'https' and not current_app.debug:
            return redirect(request.url.replace('http://', 'https://', 1), 301)
        return f(*a, **kw)
    return wrapper


def is_valid_email(email):
    return bool(VALID_EMAIL_RE.match(email))


def normalize_url_input(url):
    url = escape(url.strip())
    if not url:
        return None
    if '://' not in url:
        url = 'http://' + url
    return url
