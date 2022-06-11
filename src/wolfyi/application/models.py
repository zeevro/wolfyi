from datetime import datetime
from secrets import token_urlsafe

from flask import request
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class Invite(db.Model):
    __tablename__ = 'invites'

    id = db.Column(db.String(64), primary_key=True, default=token_urlsafe)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    used = db.Column(db.DateTime)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, nullable=False)
    password_hash = db.Column(db.String(64),  nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    urls = db.relationship('URL', cascade='all, delete-orphan')

    def __str__(self):
        return f'<User #{self.id} {self.email}>'

    def __init__(self, **kwargs):
        if 'password' in kwargs:
            self.set_password(kwargs.pop('password'))
        super().__init__(**kwargs)

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
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship('User', back_populates='urls')
    visits = db.relationship('Visit', cascade='all, delete-orphan')

    db.UniqueConstraint('user_id', 'url')

    def __str__(self):
        return f'<URL {self.id} => {self.url}>'

    def add_visit(self):
        new_visit = Visit(
            url_id=self.id,
            source_addr=request.remote_addr,
            full_url=request.url,
            referrer=request.referrer,
        )
        db.session.add(new_visit)
        db.session.commit()


class Visit(db.Model):
    __tablename__ = 'visits'

    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.String(8), db.ForeignKey('urls.id'), nullable=False)
    source_addr = db.Column(db.String(45), nullable=False)
    full_url = db.Column(db.String(255))
    referrer = db.Column(db.String(255))
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)

    url = db.relationship('URL', back_populates='visits')
