from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as UserEnum
from __init__ import db
from flask_login import UserMixin

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

class UserRole(UserEnum):
    USER = 1
    ADMIN = 2

class User (BaseModel, UserMixin):
    __table_args__ = {'extend_existing': True}

    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique= True)
    password = Column(String(50), nullable=False)
    phone = Column(String(11), nullable = False, unique = True)
    avatar = Column(String(100), nullable=True)
    email = Column(String(80))
    joined_date = Column(DateTime, default = datetime.now())
    active = Column(Boolean, default=True)
    user_role_id = Column(Enum(UserRole), default=UserRole.USER)
    ticket = relationship('Ticket', backref='user', lazy = True)

    def __str__(self):
        return self.name

class Country(BaseModel):
    __table_args__ = {'extend_existing': True}
    
    name = Column(String(30), nullable = False, unique = True)
    country = relationship('Location', backref='country', lazy = True)

    def __str__(self):
        return self.name
    
class Location(BaseModel):
    __table_args__ = {'extend_existing': True}

    city = Column(String(30), nullable = False)
    country_id = Column(Integer, ForeignKey(Country.id), nullable = False)
    airport = relationship('Airport', backref = 'location', lazy = True)



class Airport(BaseModel):
    __table_args__ = {'extend_existing': True}

    name = Column(String(50), nullable=False)
    active = Column(Boolean, default = True)
    location_id = Column(Integer, ForeignKey(Location.id), nullable = False)

    def __str__(self):
        return self.name

class Flight(BaseModel):
    __table_args__ = {'extend_existing': True}

    code = Column(String(50), nullable=False)
    from_airport = Column(Integer, ForeignKey(Airport.id), nullable = False)
    to_airport = Column(Integer, ForeignKey(Airport.id), nullable = False)
    one_class_quantity = Column(Integer, default = 1)
    second_class_quantity = Column(Integer, default = 1)
    departure_time = Column(DateTime, default = datetime.now())
    active = Column(Boolean, default = True)
    flight_time = Column(Integer, default = 60)
    ticket = relationship('Ticket', backref = 'flight', lazy = True)
    san_bay_di = relationship("Airport", foreign_keys=[from_airport])
    san_bay_den = relationship("Airport", foreign_keys=[to_airport])
    def __str__(self):
        return self.code
    
class TicketClass(BaseModel):
    __table_args__ = {'extend_existing': True}
    type = Column(String(20), nullable = False, unique = True)
    tickets = relationship('Ticket', backref='ticket_class', lazy=False)
    ticket_prices = relationship('TicketPrice', backref='ticket_class', lazy=True)

class Ticket(BaseModel):
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, ForeignKey(User.id), nullable = False)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable = False)
    ticket_class_id = Column(Integer, ForeignKey(TicketClass.id), nullable = False)
    ticket_price_id = Column(Integer, ForeignKey('ticket_price.id'), nullable = False)

class Order(BaseModel):
    __tablename__ = 'order'
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    ticket_id = Column(Integer, ForeignKey(Ticket.id), nullable = False)
    date_of_payment = Column(DateTime, default=datetime.now())
    price = Column(Float, nullable=False)
    status = Column(Boolean, default=False)
    tickets = relationship('Ticket', backref='orders', lazy=True)

class TicketPrice(BaseModel):
    __tablename__ = 'ticket_price'
    flight_id = Column(Integer, ForeignKey(Flight.id, ondelete="CASCADE"), nullable=False)
    ticket_class_id = Column(Integer, ForeignKey(TicketClass.id))
    price = Column(Float, default=0)

if __name__ == "__main__":
    db.create_all()