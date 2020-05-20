import os

import appdirs
from flask import Flask, redirect, render_template
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


db = SQLAlchemy()
login = LoginManager()


def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.url_map.strict_slashes = False
    app.url_map.converters['regex'] = RegexConverter

    app.secret_key = b'\xa3\xb7i\x00\xab\x02\xa3n\n\xb8\x0fREi\xa6zyr\x0c\x91\xd62c\x0c\x8f`\x8c\\\xd5:C\\'

    db_dir_path = appdirs.user_data_dir('wolfyi')
    os.makedirs(db_dir_path, exist_ok=True)
    db_path = os.path.join(db_dir_path, 'test.db')

    print(f'DB path: {db_path}')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}?check_same_thread=False'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login.init_app(app)

    # admin = Admin(app)

    with app.app_context():
        from . import routes
        from . import models

        db.create_all()

        # admin.add_view(ModelView(models.User, db.session))
        # admin.add_view(ModelView(models.URL, db.session))

        login.user_loader(models.User.query.get)
        login.login_view = 'login'

        return app
