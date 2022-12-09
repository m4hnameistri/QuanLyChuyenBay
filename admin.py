from __init__ import app
from flask_admin import Admin
from models import *
from flask_admin.contrib.sqla import ModelView

admin = Admin(app = app, name = "Flight Management Administration", template_mode = 'bootstrap4')
admin.add_view(ModelView(Flight, db.session))
admin.add_view(ModelView(Airport, db.session))
admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(Country, db.session))

