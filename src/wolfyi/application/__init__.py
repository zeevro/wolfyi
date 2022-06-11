import os

import appdirs
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

from .utils import RegexConverter, format_date


db = SQLAlchemy()
login = LoginManager()


def create_app(echo=False):
    app = Flask(__name__, template_folder='../templates')
    app.url_map.strict_slashes = False
    app.url_map.converters['regex'] = RegexConverter
    app.add_template_filter(format_date, 'format_date')

    app.secret_key = b'\xa3\xb7i\x00\xab\x02\xa3n\n\xb8\x0fREi\xa6zyr\x0c\x91\xd62c\x0c\x8f`\x8c\\\xd5:C\\'

    app.wsgi_app = ProxyFix(app.wsgi_app)

    db_dir_path = appdirs.site_data_dir('wolfyi')
    os.makedirs(db_dir_path, exist_ok=True)
    db_path = os.path.join(db_dir_path, 'test.db')

    if echo:
        print(f'DB path: {db_path}')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}?check_same_thread=False'
    app.config['SQLALCHEMY_ECHO'] = echo
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login.init_app(app)
    login.login_view = 'login'

    with app.app_context():
        from . import admin, models, routes  # Must import admin & routes here for them to register

        db.create_all()

        login.user_loader(models.User.query.get)

        admin.admin.init_app(app)

    return app
