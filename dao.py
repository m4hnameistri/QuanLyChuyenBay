from models import Location, Country, Flight, Airport, User, Ticket, TicketClass, TicketPrice, UserRole, TuyenBay, SanBayTrungGian
from __init__ import db
from sqlalchemy.orm import aliased
from flask_login import current_user
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.sql import extract
from cryptography.hazmat.backends import default_backend
import hashlib


def load_location():
    return Location.query.all()

def load_countries():
    return Country.query.all()

def load_airports():
    return Airport.query.all()

def load_airports_city():
    return db.session.query(Airport.id, Airport.name, Location.id, Location.city)\
                    .join(Location, Airport.location_id == Location.id)\
                    .all()

def load_user():
    return User.query.all()

def load_ticket_class():
    return TicketClass.query.all()

def load_ticket_price():
    return TicketPrice.query.all()

def get_ticket_price_by_id(flight_id = None, ticket_class_id = None):
    q = TicketPrice.query
    if flight_id:
        q = q.filter(TicketPrice.flight_id.__eq__(flight_id))
    if ticket_class_id:
        q = q.filter(TicketPrice.ticket_class_id.__eq__(ticket_class_id))
    return q.all()
def get_airport_by_id(airport_id):
    return Airport.query.get(airport_id)

def get_flight_by_id(flight_id):
    return Flight.query.get(flight_id)

def count_ticket_by_flight(flight_id):
    return db.session.query(Flight.id, func.count(Ticket.id))\
                    .join(Ticket, Ticket.flight_id == Flight.id)\
                    .filter(Flight.id == flight_id)\
                    .group_by(Flight.id).all()

def count_ticket_by_ticket_class(flight_id, ticket_class_id):
    return db.session.query(Flight.id, func.count(Ticket.id))\
                    .join(Flight, Ticket.flight_id == Flight.id)\
                    .filter(Ticket.flight_id == flight_id)\
                    .filter(Ticket.ticket_class_id == ticket_class_id)\
                    .first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_ticket_by_id(flight_id):
    return Ticket.query.filter(flight_id = flight_id)
    
def load_flights(from_country = None, to_country = None, departure_date = None, code = None):
    a1 = aliased(Airport)
    a2 = aliased(Airport)
    lo1 = aliased(Location)
    lo2 = aliased(Location)
    c1 = aliased(Country)
    c2 = aliased(Country)
    # f = db.session.query(Flight.code, Flight.from_airport, Flight.to_airport, Flight.departure_time, Flight.one_class_quantity, Flight.second_class_quantity)\
    #     .join(Airport, Flight.from_airport == Airport.id , isouter = True)\
    #     .join(Location, Location.id == Airport.location_id, isouter = True)\
    #     .join(Country, Country.id == Location.country_id, isouter = True)\
    #     .join(Airport, Flight.to_airport == Airport.id , isouter = True)\
    #     .join(Location, Location.id == Airport.location_id, isouter = True)\
    #     .join(Country, Country.id == Location.country_id, isouter = True)\

    f = db.session.query(Flight.id, Flight.code, Flight.from_airport, Flight.to_airport, Flight.departure_time, Flight.flight_time, Flight.one_class_quantity, Flight.second_class_quantity)\
        .join(a1, Flight.from_airport == a1.id , isouter = True)\
        .join(lo1, lo1.id == a1.location_id, isouter = True)\
        .join(c1, c1.id == lo1.country_id, isouter = True)\
        .join(a2, Flight.to_airport == a2.id , isouter = True)\
        .join(lo2, lo2.id == a2.location_id, isouter = True)\
        .join(c2, c2.id == lo2.country_id, isouter = True)\

    if departure_date:
        f = f.filter(Flight.departure_time.__gt__(departure_date))

    if code:
        f = f.filter(Flight.code.contains(code))
        
    if from_country and to_country:
        f = f.filter(c1.id == from_country)
        f = f.filter(c2.id == to_country)
        return f.all()
    return f.all()

def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name = name.strip(),
                username = username.strip(),
                password = password,
                phone = kwargs.get('phone'),
                avatar = kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()

# def check_login(username, password, role = UserRole.USER):
#     if username and password:
#         password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
#         return User.query.filter(User.username.__eq__(username.strip()),
#                                 User.password.__eq__(password),
#                                 User.user_role_id.__eq__(role)).first()
    

def check_login(username, password, role = UserRole.USER):
    q = User.query
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        q = q.filter(User.username.__eq__(username.strip()),
                                User.password.__eq__(password))
    if role == UserRole.ADMIN:
        q = q.filter(User.user_role_id.__eq__(role))
    return q.first()

def add_ticket(flight_id, ticket_class_id, ticket_price_id):
    t = Ticket(user_id = current_user.id, flight_id = flight_id, ticket_class_id = ticket_class_id, ticket_price_id = ticket_price_id)
    db.session.add(t)
    db.session.commit()

# def add_order(flight_id, ticket_id, price):
#     o = Order(user_id = current_user, ticket_id = ticket_id, price = price )
#     db.session.add(o)
#     db.session.commit()


# def sth():
#     from_airports = []
#     to_airports = []
#     locations = load_location()
#     countries = load_countries()
#     airports = load_airports()
#     flights = load_flights(from_country= 1, to_country= 1)

#     for flight in flights:
#         from_airport = get_airport_by_id(flight.from_airport)
#         to_airport = get_airport_by_id(flight.to_airport)

#         from_airports.append(from_airport)
#         to_airports.append(to_airport)

#     from_to = list(zip(flights,from_airports, to_airports))
#     for fl in flights:
#         print(fl)

def add_flight(code = None, from_airport = None, to_airport = None, one_class_quantity = None, second_class_quantity = None, departure_date = None, flight_time = None):
    # date_time_str = '15/11/22 19:15:00'

    date_time_obj = datetime.strptime(departure_date, '%Y-%m-%dT%H:%M')
    c = Flight(code = code, from_airport = from_airport, to_airport = to_airport, departure_time = date_time_obj, one_class_quantity = one_class_quantity, second_class_quantity = second_class_quantity, flight_time = flight_time, tuyen_bay_id = 1)
    db.session.add(c)
    db.session.commit()

def delete_flight(flight_id):
    d = db.session.query(Flight).filter(Flight.id== flight_id).first()
    db.session.delete(d)
    db.session.commit()

def add_inter_airport(flight_id, airport_id, thoi_gian_dung = None, ghi_chu = None):
    a = SanBayTrungGian(flight_id = flight_id, airport_id = airport_id, thoi_gian_dung = thoi_gian_dung, ghi_chu = ghi_chu)
    db.session.add(a)
    db.session.commit()

def get_latest_flight_id():
    return Flight.query.filter(Flight.id == db.session.query(func.max(Flight.id))).first()

def flight_stats():
    # return Flight.query.join(Ticket, Ticket.flight_id.__eq__(Flight.id), isouter = True).add_columns(func.count(Ticket.id))\
    #                 .group_by(Flight.id, Flight.departure_time).all()
    return db.session.query(Flight.id, Flight.code, Flight.departure_time, Flight.one_class_quantity, Flight.second_class_quantity,func.count(Ticket.id).label('So luong ve da ban'), func.sum(TicketPrice.price))\
                     .join(Ticket, Ticket.flight_id == Flight.id, isouter = True)\
                     .join(TicketPrice, TicketPrice.id == Ticket.ticket_price_id, isouter = True)\
                     .group_by(Flight.id, Flight.departure_time).all()

def avenue_month_stats(month = None, from_date = None, to_date = None):
    s = db.session.query(TuyenBay.id, TuyenBay.name, func.count(func.distinct(Ticket.id)), func.sum(TicketPrice.price))\
                .join(Flight, Flight.tuyen_bay_id == TuyenBay.id, isouter = True)\
                .join(TicketPrice, TicketPrice.flight_id == Flight.id)\
                .join(Ticket, Ticket.ticket_price_id == TicketPrice.id)\
                .group_by(TuyenBay.id, TuyenBay.name)
    if month:
        s = s.filter(extract('month', Ticket.date_of_payment).__eq__(month))
    if from_date:
        s = s.filter(Ticket.date_of_payment.__ge__(from_date))
    
    if to_date:
        s = s.filter(Ticket.date_of_payment.__le__(to_date))

    return s.all()

def load_sth(kw = None):
    u = User.query.filter(User.name.contains(kw))
    return u

if __name__ == "__main__":
    # print(load_flights(from_country = 1,to_country = 1))
    t = get_ticket_price_by_id(flight_id = 11, ticket_class_id=1)
    print(t)
    # print(count_ticket_by_ticket_class(flight_id=13, ticket_class_id= 1)[1])
    # a = [4,6]
    # print(load_sth(kw= 'Kha'))