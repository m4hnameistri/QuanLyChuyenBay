from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = "@#!123125539%$@"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:213203@localhost/chuyenbaydb?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app = app)
cloudinary.config(
    cloud_name = 'dfrindwbb',
    api_key = '289596259831969', 
    api_secret = 'hK_k5l9u-ApCZgJoRkqf09TLYwQ'
)

login = LoginManager(app = app)
# import dao

# @app.route("/")
# def index():
#     locations = dao.load_location()
#     countries = dao.load_countries()
#     # flights = dao.load_flights()

#     return render_template('index.html', locations = locations, countries = countries)

# if __name__ == "__main__":
#     app.run(debug=True)