from flask import render_template, request, redirect, session, jsonify, url_for
import dao
from __init__ import app, login
from flask_login import login_user, logout_user, login_required
from models import UserRole
import cloudinary.uploader

# @app.route("/")
# def index():
#     locations = dao.load_location()
#     return render_template('index.html', locations = locations )
@app.route("/")
def index():
    from_country = request.args.get('from_country')
    to_country = request.args.get('to_country')
    departure_date = request.args.get('departure_date')

    from_airports = []
    to_airports = []
    locations = dao.load_location()
    countries = dao.load_countries()
    airports = dao.load_airports()
    flights = dao.load_flights(from_country= from_country, to_country= to_country, departure_date=departure_date)

    for flight in flights:
        from_airport = dao.get_airport_by_id(flight.from_airport)
        to_airport = dao.get_airport_by_id(flight.to_airport)

        from_airports.append(from_airport)
        to_airports.append(to_airport)

    chuyenbay = list(zip(flights, from_airports, to_airports))
    return render_template('index.html', locations = locations, countries = countries, airports = airports, chuyenbay = chuyenbay)

@app.route("/flight/flight_id=<int:flight_id>")
def flight_detail(flight_id):
    flight = dao.get_flight_by_id(flight_id)
    ticket_class = dao.load_ticket_class()
    ticket_prices = dao.get_ticket_price_by_id(flight_id= flight_id)
    from_airport = dao.get_airport_by_id(flight.from_airport)
    to_airport = dao.get_airport_by_id(flight.to_airport)
    return render_template('flight_detail.html', flight = flight, from_airport = from_airport, to_airport = to_airport, ticket_class = ticket_class, ticket_prices = ticket_prices)
    

@app.route('/register', methods = ['get', 'post'])
def user_register():
    err_msg = ""
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        phone = request.form.get('phone')
        confirm = request.form.get('confirm')
        avatar_path = None
        try:
            for u in dao.load_user():
                if u.username == username:
                    err_msg = "Username này đã có người sử dụng !"
                    break
                if u.phone == phone:
                    err_msg = "Số điện thoại này đã có người sử dụng !"
                    break
            if not password.strip().__eq__(confirm.strip()):
                err_msg = 'Mật khẩu không khớp !'
            if len(err_msg) == 0:
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                dao.add_user(name = name, username= username, password=password, phone = phone, avatar = avatar_path)
                return redirect(url_for('index'))

        except Exception as ex:
            err_msg = "Hệ thống có lỗi" + str(ex)

    return render_template('/user/register.html', err_msg = err_msg)

@app.route("/signin", methods = ['get', 'post'])
def user_signin():
    err_msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.check_login(username=username, password=password)
        if user:
            login_user(user = user)
            return redirect(url_for('index'))
        else:
            err_msg = 'Username hoặc password không chính xác !'
    return render_template('/user/login.html', err_msg = err_msg)

@app.route('/admin-signin', methods=['get','post'])
def admin_signin():
    # if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.check_login(username=username, password=password, role=UserRole.ADMIN)
        if user:
            login_user(user = user)
        return redirect('/admin')

@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))

@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id = user_id)

@app.route('/api/pay')
@login_required
def pay():
    # if request.method == 'POST':
        flight_id = request.args.get('flight_id')
        ticket_class_id = request.args.get('ticket_class')
        ticket_price = dao.get_ticket_price_by_id(flight_id= flight_id, ticket_class_id = ticket_class_id)
        ticket = dao.add_ticket(flight_id= flight_id, ticket_class= ticket_class_id, ticket_price= ticket_price)

        # try:
        #     ticket = dao.add_ticket(flight_id= flight_id, ticket_class= ticket_class_id, ticket_price= ticket_price)
        #     return jsonify({'status': 200})
        # except Exception as ex:
        #     print(str(ex))
        #     return jsonify({'status': 500})
        return render_template('flight_detail.html',flight_id = flight_id, ticket_class_id = ticket_class_id)

@app.route('/api/payment', methods=['post'])
@login_required
def payment():
        msg = ''
        data = request.json

        flight_id = data['flight_id']
        ticket_class_id = data['ticket_class_id']
        ticket_price_id = data['ticket_price_id']

        fl = dao.get_flight_by_id(flight_id= flight_id)
        # Tính khoảng cách ngày khởi hành và thời gian hiện tại
        diff = fl.departure_time - datetime.now()
        sec = diff.total_seconds()

        # Tính số lượng vé đã được đặt của mỗi chuyến bay
        ticket_quantity = dao.count_ticket_by_flight(flight_id= flight_id)
        ticket_quantity = ticket_quantity[0][1]
        # chỉ đặt cho các chuyến bay trước 12h (43200 s) lúc khởi hành.
        try:
            if sec <= 43200 :
                msg = "Chỉ được đặt các chuyến bay trước 12h lúc khởi hành !!!"
                return jsonify({'msg' : msg})
            elif ticket_quantity >= (fl.one_class_quantity + fl.second_class_quantity):
                msg = "Đã hết vé ! Vui lòng chọn chuyến bay khác"
                return jsonify({'msg' : msg})
            else:
                ticket = dao.add_ticket(flight_id= flight_id, ticket_class_id= ticket_class_id, ticket_price_id= ticket_price_id)
                return jsonify({'status': 200})
        except Exception as ex:
            print(str(ex))
            return jsonify({'status': 500})



if __name__ == "__main__":
    from admin import *
    app.run(debug = True)