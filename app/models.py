from app import db
from app import login

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

import sqlalchemy.dialects.postgresql


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(3), index=True, unique=True)
    code = db.Column(db.Integer, index=True, unique=True)
    payway = db.Column(db.String(16), index=True, unique=True)


    def __repr__(self):
        return f'<{self.name} -- {self.code}>'


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(5,2), index=True)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    stime = db.Column(db.TIMESTAMP, index=True)
    currency = db.relationship('Currency', backref='order')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='order')


@login.user_loader
def load_user(id_):
    return Users.query.get(int(id_))
        