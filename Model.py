import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate # is this necessary?
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

ma = Marshmallow()
db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def encode_auth_token(self, user_id):
		# try:
		payload = {
			'exp': (datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=60*60) - datetime.datetime(1970,1,1)).total_seconds(),
			'iut': (datetime.datetime.utcnow() - datetime.datetime(1970,1,1)).total_seconds(),
			'sub': user_id
		}
		return jwt.encode(
			payload,
			current_app.config.get('SECRET_KEY'),
			algorithm='HS256'
		)
		# except Exception as e:
		# 	return e

	@staticmethod
	def decode_auth_token(auth_token):
		try:
			payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
			return payload['sub']
		except jwt.ExpiredSignatureError:
			return 'Signature expired. Please log in again.'
		except jwt.InvalidTokenError:
			return 'Invalid token. Please log in again.'

class UserSchema(ma.Schema):
	id = fields.Integer()
	username = fields.String() # check doc: setting required=True/False doesn't seem to do anything
	email = fields.String()
	password = fields.String()
	password_hash = fields.String()

class PrivateUserSchema(ma.Schema):
	username = fields.String()

class PublicUserSchema(ma.Schema):
	username = fields.String()