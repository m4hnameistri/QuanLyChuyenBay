from flask import render_template, request, redirect, session, jsonify, url_for
import dao
from __init__ import app, login
from flask_login import login_user, logout_user, login_required
from models import UserRole
from datetime import datetime
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

@app.context_processor
def common_attributes():
    airports = dao.load_airports_city()
    
    return {
        'airports': airports,
        'role' : UserRole
    }

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
                return redirect(url_for('user_signin'))

        except Exception as ex:
            err_msg = "Hệ thống có lỗi" + str(ex)

    return render_template('/user/register.html', err_msg = err_msg)

@app.route("/flight/flight_list")
@login_required
def flight_list():
    if current_user.user_role_id == UserRole.EMPLOYEE or current_user.user_role_id == UserRole.ADMIN:
        flight_code = request.args.get('flight_code')
        departure_date = request.args.get('departure_date')

        from_airports = []
        to_airports = []
        flights = dao.load_flights(departure_date=departure_date, code = flight_code)

        for flight in flights:
            from_airport = dao.get_airport_by_id(flight.from_airport)
            to_airport = dao.get_airport_by_id(flight.to_airport)

            from_airports.append(from_airport)
            to_airports.append(to_airport)

        chuyenbay = list(zip(flights, from_airports, to_airports))
        return render_template("flight_list.html", chuyenbay = chuyenbay)
    return redirect('/')
@app.route("/api/add_flight", methods=['get','post'])
@login_required
def add_flight():
    err_msg = ""
    trung_gian_quantity = 2
    if request.method == 'POST':
        code = str(request.form.get('code'))
        from_airport = request.form.get('from_airport')
        to_airport = request.form.get('to_airport')
        departure = request.form.get('departure_date')
        flight_time = request.form.get('flight_time')
        one_quantity = request.form.get('one_quantity')
        second_quantity = request.form.get('second_quantity')

        inter_airports=[]
        ia_airport_id =[]
        ia_flight_id =[]
        for f in dao.load_flights():
            if f.code == code:
                err_msg += "Đã tồn tại mã chuyến bay này !\n"
                break
        if from_airport == to_airport:
            err_msg += "Sân bay đi và đến không được trùng nhau!"
        elif datetime.strptime(departure, '%Y-%m-%dT%H:%M').__le__(datetime.now()):
            err_msg += "Ngày giờ khởi hành KHÔNG được nhỏ hơn thời gian hiện tại !"

        if len(err_msg) == 0:
            try:
                dao.add_flight(code = code, from_airport = from_airport, to_airport = to_airport, one_class_quantity = one_quantity, second_class_quantity = second_quantity, departure_date = departure, flight_time = flight_time)
                for i in range(trung_gian_quantity):
                    a_id = request.form.get('inter_airport' + str(i))
                    f_id = dao.get_latest_flight_id().id
                    stop_time = request.form.get('stop_time' + str(i))
                    note = request.form.get('note' + str(i))

                    dao.add_inter_airport(airport_id= a_id, flight_id= f_id, thoi_gian_dung= stop_time, ghi_chu= note)

                return redirect(url_for('flight_list'))  
            except Exception as ex:
                err_msg = "Hệ thống có lỗi" + str(ex)

    return render_template('add_flight.html', err_msg = err_msg, trung_gian_quantity = trung_gian_quantity)


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

# @app.route('/api/pay')
# @login_required
# def pay():
#     # if request.method == 'POST':
#         flight_id = request.args.get('flight_id')
#         ticket_class_id = request.args.get('ticket_class')
#         ticket_price = dao.get_ticket_price_by_id(flight_id= flight_id, ticket_class_id = ticket_class_id)
#         ticket = dao.add_ticket(flight_id= flight_id, ticket_class= ticket_class_id, ticket_price= ticket_price)

#         # try:
#         #     ticket = dao.add_ticket(flight_id= flight_id, ticket_class= ticket_class_id, ticket_price= ticket_price)
#         #     return jsonify({'status': 200})
#         # except Exception as ex:
#         #     print(str(ex))
#         #     return jsonify({'status': 500})
#         return render_template('flight_detail.html',flight_id = flight_id, ticket_class_id = ticket_class_id)

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
        ticket_quantity_by_class = dao.count_ticket_by_ticket_class(flight_id=flight_id, ticket_class_id= ticket_class_id)

        # ticket_quantity_2 = dao.count_ticket_by_ticket_class(flight_id=flight_id, ticket_class_id= ticket_class_id)
        if ticket_quantity and ticket_quantity_by_class:
            ticket_quantity = ticket_quantity[0][1]
            ticket_quantity_by_class = ticket_quantity_by_class[1]
        else:   
            ticket_quantity = 0
            ticket_quantity_by_class = 0
        # ticket_quantity_2 = ticket_quantity_2[0][1]
        # chỉ đặt cho các chuyến bay trước 12h (43200 s) lúc khởi hành.
        try:
            if sec <= 43200 :
                msg = "Chỉ được đặt các chuyến bay trước 12h lúc khởi hành !!!"
                return jsonify({'msg' : msg})
            elif ticket_quantity >= (fl.one_class_quantity + fl.second_class_quantity):
                msg = "Chuyến bay này đã hết vé! Vui lòng chọn chuyến bay khác"
                return jsonify({'msg' : msg})
            elif ticket_class_id == '1' and ticket_quantity_by_class >= fl.one_class_quantity:
                msg = "Đã hết vé hạng {}! Vui lòng chọn vé hạng khác".format(ticket_class_id)
                return jsonify({'msg' : msg})
            elif ticket_class_id == '2' and ticket_quantity_by_class >= fl.second_class_quantity:
                msg = "Đã hết vé hạng {}! Vui lòng chọn vé hạng khác".format(ticket_class_id)
                return jsonify({'msg' : msg})
            else:
                dao.add_ticket(flight_id= flight_id, ticket_class_id= ticket_class_id, ticket_price_id= ticket_price_id)
                return jsonify({'status': 200})
        except Exception as ex:
            print(str(ex))
            return jsonify({'status': 500})

@app.route("/my-ticket", methods=['get'])
@login_required
def my_ticket():
    prices = []
    for t in current_user.ticket:
        prices.append(dao.get_ticket_price_by_id(flight_id = t.flight_id, ticket_class_id= t.ticket_class_id))
    data = list(zip(current_user.ticket, prices))
    return render_template('my_ticket.html', data = data) 

@app.route('/api/delete-flight/<flight_id>', methods=['delete'])
def delete_flight(flight_id):
    try:
        dao.delete_flight(flight_id= flight_id)
        return jsonify({'status': 200})    
    except Exception as ex:
        return jsonify({'msg': str(ex)})


if __name__ == "__main__":
    from admin import *
    app.run(debug = True)