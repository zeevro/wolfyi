from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

from .utils import RegexConverter, format_date


login = LoginManager()


def create_app() -> Flask:
    app = Flask(__name__, template_folder='../templates')
    app.url_map.strict_slashes = False
    app.url_map.converters['regex'] = RegexConverter
    app.add_template_filter(format_date, 'format_date')

    app.secret_key = b'\xa3\xb7i\x00\xab\x02\xa3n\n\xb8\x0fREi\xa6zyr\x0c\x91\xd62c\x0c\x8f`\x8c\\\xd5:C\\'

    app.wsgi_app = ProxyFix(app.wsgi_app)

    login.init_app(app)
    login.login_view = 'login'

    with app.app_context():
        from .models import User, create_tables
        login.user_loader(User.get_by_id)
        create_tables()

        from .admin import admin
        admin.init_app(app)

        from . import routes  # Must import routes here for them to register

    return app
