from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView

from .models import URL, Invite, User, Visit


admin = Admin()


class InviteModelView(ModelView):
    pass


class UserModelView(ModelView):
    column_exclude_list = ['password_hash']
    column_searchable_list = [User.email]


class UrlModelView(ModelView):
    column_searchable_list = [URL.id, URL.url]


class VisitModelView(ModelView):
    column_searchable_list = [URL.id, URL.url, Visit.source_addr, Visit.full_url, Visit.referrer]


admin.add_view(InviteModelView(Invite))
admin.add_view(UserModelView(User))
admin.add_view(UrlModelView(URL))
admin.add_view(VisitModelView(Visit))
