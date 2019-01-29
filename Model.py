from flask import Flask # is this necessary?
from marshmallow import Schema, fields, pre_load, validate # is this necessary?
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

ma = Marshmallow()
db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	def __repr__(self):
		return '<User {}>'.format(self.username)

class UserSchema(ma.Schema):
	id = fields.Integer()
	username = fields.String() # check doc: setting required=True/False doesn't seem to do anything
	email = fields.String()
