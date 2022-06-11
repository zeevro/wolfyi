from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from . import db, models


admin = Admin()


class MyModelView(ModelView):
    column_display_pk = True

    def is_accessible(self):
        try:
            return current_user.is_authenticated and current_user.is_admin
        except Exception:
            return False


class InviteModelView(MyModelView):
    pass


class UserModelView(MyModelView):
    column_searchable_list = ['email']
    form_excluded_columns = ['urls']


class UrlModelView(MyModelView):
    column_searchable_list = ['id', 'url']
    form_excluded_columns = ['visits']


class VisitModelView(MyModelView):
    column_searchable_list = ['url.id', 'url.url', 'source_addr', 'full_url', 'referrer']


admin.add_view(InviteModelView(models.Invite, db.session))
admin.add_view(UserModelView(models.User, db.session))
admin.add_view(UrlModelView(models.URL, db.session))
admin.add_view(VisitModelView(models.Visit, db.session))
