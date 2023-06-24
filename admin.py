from __init__ import app, db
from flask_admin import Admin
from flask_admin import BaseView, expose, AdminIndexView
from models import *
import dao
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect, request


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role_id.__eq__(UserRole.ADMIN)

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats = dao.flight_stats())
        
class StatsView(BaseView):
    @expose('/')
    def index(self):
        month = request.args.get('month')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        return self.render('admin/stats.html', stats = dao.avenue_month_stats(month= month, from_date= from_date, to_date= to_date))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role_id.__eq__(UserRole.ADMIN)

admin = Admin(app = app, name = "Flight Management Administration", template_mode = 'bootstrap4', index_view = MyAdminIndex())

admin.add_view(AuthenticatedModelView(Flight, db.session))
admin.add_view(AuthenticatedModelView(Airport, db.session))
admin.add_view(AuthenticatedModelView(Location, db.session))
admin.add_view(AuthenticatedModelView(Country, db.session))
admin.add_view(StatsView(name = 'Stats'))
admin.add_view(LogoutView(name = 'Logout'))
