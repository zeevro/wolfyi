from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(64), nullable=False)
    created = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    urls = db.relationship('URL')

    def __init__(self, email, password):
        self.email = email
        self.created = datetime.utcnow()
        self.set_password(password)

    def set_password(self, password, save=False):
        self.password_hash = generate_password_hash(password)
        if save:
            self.save()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class URL(db.Model):
    __tablename__ = 'urls'

    id = db.Column(db.String(8), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    url = db.Column(db.Text, index=False, unique=False, nullable=False)
    created = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    db.UniqueConstraint('user_id', 'url')
