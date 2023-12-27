# import logging
from pathlib import Path
from secrets import token_urlsafe
from typing import TYPE_CHECKING, Any

from appdirs import site_data_dir
from flask import request
from flask_login import UserMixin
from peewee import BooleanField, CharField, ForeignKeyField, Model, SqliteDatabase, TextField, TimestampField
from werkzeug.security import check_password_hash, generate_password_hash


# logging.basicConfig()
# logging.getLogger('peewee').setLevel(logging.DEBUG)


db_path = Path(site_data_dir('wolfyi')) / 'test.db'

database = SqliteDatabase(db_path, pragmas={'foreign_keys': 1})
database.connection().set_trace_callback(print)


def create_tables():
    database.create_tables([User, URL, Visit, Invite])


def table_function(model: type[Model]):
    return f'{model.__name__.lower()}s'


class BaseModel(Model):
    class Meta:
        database = database
        table_function = table_function

    if TYPE_CHECKING:
        id: Any


class User(UserMixin, BaseModel):
    email = CharField(max_length=128, unique=True)
    password_hash = CharField(max_length=256)
    created = TimestampField(utc=True)
    is_admin = BooleanField(default=False)

    def set_password(self, password: str, save: bool = False) -> bool | int:
        self.password_hash = generate_password_hash(password)
        return save and self.save()

    password = property(None, set_password)  # type: ignore

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)  # type: ignore

    def __str__(self) -> str:
        return f'#{self.id} {self.email}'


class URL(BaseModel):
    class Meta:
        indexes = [(('user', 'url'), True)]

    id = CharField(primary_key=True, max_length=8, default=lambda: token_urlsafe()[:6])
    user = ForeignKeyField(User, backref='urls', on_delete='CASCADE')
    url = TextField()
    created = TimestampField(utc=True)

    def __str__(self) -> str:
        return f'{self.id} -> {self.url}'

    def add_visit(self) -> 'Visit':
        return Visit.create(
            url=self,
            source_addr=request.remote_addr,
            full_url=request.url,
            referrer=request.referrer,
        )


class Visit(BaseModel):
    url = ForeignKeyField(URL, backref='visits', on_delete='CASCADE')
    source_addr = CharField(max_length=45)
    full_url = CharField(max_length=255)
    referrer = CharField(max_length=255)
    created = TimestampField(utc=True)

    def __str__(self) -> str:
        return f'{self.url}'


class Invite(BaseModel):
    id = CharField(primary_key=True, max_length=64, default=token_urlsafe)
    created = TimestampField(utc=True)
    used = TimestampField(utc=True, null=True)
    used_by = ForeignKeyField(User)
