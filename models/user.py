import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate # is this necessary?
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
#from Following import Following, FollowingAggregation
import jwt

from models.shared import db

ma = Marshmallow()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), unique=True)
	password_hash = db.Column(db.String(128))
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	privacy = db.Column(db.Boolean)
	created_at = db.Column(db.DateTime)
	updated_at = db.Column(db.DateTime)
	profile_pic = db.Column(db.LargeBinary)
	posts = db.relationship("Post")

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	# def follow(self, person):
	# 	following_relation = Following(self.id, person.id)
	# 	Following.add(following_relation)

	# 	db.session.query(FollowingAggregation).filter(FollowingAggregation.user_id == self.id).update({FollowingAggregation.following: FollowingAggregation.following + 1})
	# 	db.session.query(FollowingAggregation).filter(FollowingAggregation.user_id == person.id).update({FollowingAggregation.followers: FollowingAggregation.followers + 1})

	# 	db.session.commit()

	# def unfollow(self, person):
	# 	db.session.query(Following).filter(Following.user_id == self.id, Following.following_id == person.id).delete()

	# 	db.session.query(FollowingAggregation).filter(FollowingAggregation.user_id == self.id).update({FollowingAggregation.following: FollowingAggregation.following - 1})
	# 	db.session.query(FollowingAggregation).filter(FollowingAggregation.user_id == person.id).update({FollowingAggregation.followers: FollowingAggregation.followers - 1})

	# 	db.session.commit()

	def encode_auth_token(self, user_id):
		# try:
		payload = {
			'exp': (datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0) - datetime.datetime(1970,1,1)).total_seconds(),
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

# master schema
class UserSchema(ma.Schema):
	id = fields.Integer()
	username = fields.String()
	email = fields.String()
	password = fields.String()
	password_hash = fields.String()
	first_name = fields.String()
	last_name = fields.String()
	privacy = fields.Boolean()
	created_at = fields.DateTime()
	updated_at = fields.DateTime()
	profile_pic = fields.Raw()

class UserRegisterSchema(ma.Schema):
	username = fields.String(required=True)
	email = fields.String(required=True)
	password = fields.String(required=True)
	first_name = fields.String(required=True)
	last_name = fields.String(required=True)

class UserLoginSchema(ma.Schema):
	username = fields.String(required=True)
	email = fields.String()
	password = fields.String(required=True, load_only=True)
	first_name = fields.String()
	last_name = fields.String()
	privacy = fields.Boolean()
	created_at = fields.DateTime()
	updated_at = fields.DateTime()

class OwnerUserSchema(ma.Schema):
	username = fields.String()
	email = fields.String()
	first_name = fields.String()
	last_name = fields.String()
	privacy = fields.Boolean()
	created_at = fields.DateTime()
	updated_at = fields.DateTime()
	profile_pic = fields.Raw()

class PrivateUserSchema(ma.Schema):
	username = fields.String()
	email = fields.String()
	first_name = fields.String()
	last_name = fields.String()
	profile_pic = fields.Raw()

class PublicUserSchema(ma.Schema):
	username = fields.String()
	profile_pic = fields.Raw()

class SearchUserSchema(ma.Schema):
	username = fields.String()