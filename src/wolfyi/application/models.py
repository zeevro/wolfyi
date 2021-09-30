from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class Invite(db.Model):
    __tablename__ = 'invites'

    id = db.Column(db.String(64), primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.DateTime)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, nullable=False)
    password_hash = db.Column(db.String(64),  nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    url = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates='urls')
    visits = db.relationship('Visit')

    db.UniqueConstraint('user_id', 'url')


class Visit(db.Model):
    __tablename__ = 'visits'

    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.String(8), db.ForeignKey('urls.id'), nullable=False)
    source_addr = db.Column(db.String(45), nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    url = db.relationship('URL', back_populates='visits')
