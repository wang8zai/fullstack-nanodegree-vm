import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import random
import string
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase +
                     string.digits) for x in xrange(32))


class User(Base):
    """
    User defines a user.
    name is user name.
    name and password_hash is mainly used to identify user.
    hassword_hash is a encrpyed password by SHA256.
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    # get encryped password
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    # verify encrpyed password
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    # generate token.
    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    # verify token.
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        user_id = data['id']
        return user_id

    # serialize data.
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'picture': self.picture,
            'email': self.email
        }


class Owner(Base):
    """
    Catalog class.
    user_id shares relationship to is in User.
    """
    __tablename__ = 'owner'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id
        }


class Item(Base):
    """
    Item class.
    describes an item from description,
    name, price and rate.
    description, name and created data are commonly used.
    """
    __tablename__ = 'item'

    name = Column(String(80), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(Integer, default=0)
    rate = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey('owner.id'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    owner = relationship(Owner)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'rate': self.rate,
            'created_date': self.created_date,
            'owner_id': self.owner_id,
            'user_id': self.user_id
        }


engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)
