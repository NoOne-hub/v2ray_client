"""
    flask.ext.basicauth
    ~~~~~~~~~~~~~~~~~~~

    Flask-BasicAuth is a Flask extension that provides an easy way to protect
    certain views or your whole application with HTTP basic access
    authentication.

    :copyright: (c) 2013 Janne Vanhala.
    :license: BSD, see LICENSE for more details.
"""
import base64
from functools import wraps

from flask import current_app, request, Response


__version__ = '0.2.0'


class BasicAuth(object):
    """
    A Flask extension for adding HTTP basic access authentication to the
    application.

    :param app: a :class:`~flask.Flask` instance. Defaults to `None`. If no
        application is provided on creation, then it can be provided later on
        via :meth:`init_app`.
    """
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        """
        Initialize this BasicAuth extension for the given application.

        :param app: a :class:`~flask.Flask` instance
        """
        app.config.setdefault('BASIC_AUTH_FORCE', False)
        app.config.setdefault('BASIC_AUTH_REALM', '')

        @app.before_request
        def require_basic_auth():
            if not current_app.config['BASIC_AUTH_FORCE']:
                return
            if not self.authenticate():
                return self.challenge()

    def check_credentials(self, username, password):
        """
        Check if the given username and password are correct.

        By default compares the given username and password to
        ``HTTP_BASIC_AUTH_USERNAME`` and ``HTTP_BASIC_AUTH_PASSWORD``
        configuration variables.

        :param username: a username provided by the client
        :param password: a password provided by the client
        :returns: `True` if the username and password combination was correct,
            and `False` otherwise.
        """
        correct_username = current_app.config['BASIC_AUTH_USERNAME']
        correct_password = current_app.config['BASIC_AUTH_PASSWORD']
        return username == correct_username and password == correct_password

    def authenticate(self):
        """
        Check the request for HTTP basic access authentication header and try
        to authenticate the user.

        :returns: `True` if the user is authorized, or `False` otherwise.
        """
        auth = request.authorization
        return (
            auth and auth.type == 'basic' and
            self.check_credentials(auth.username, auth.password)
        )

    def challenge(self):
        """
        Challenge the client for username and password.

        This method is called when the client did not provide username and
        password in the request, or the username and password combination was
        wrong.

        :returns: a :class:`~flask.Response` with 401 response code, including
            the required authentication scheme and authentication realm.
        """
        realm = current_app.config['BASIC_AUTH_REALM']
        return Response(
            status=401,
            headers={'WWW-Authenticate': 'Basic realm="%s"' % realm}
        )

    def required(self, view_func):
        """
        A decorator that can be used to protect specific views with HTTP
        basic access authentication.
        """
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if self.authenticate():
                return view_func(*args, **kwargs)
            else:
                return self.challenge()
        return wrapper
