import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

ma = Marshmallow()

class Hashtag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	hashtag = db.Column(db.String(30), unique=True)
	# Note: could not create table with hashtag being primary key as well
	# post_hashtag refs hashtag as a foreign key and foreign keys must be unique
	# having id and hashtag both as primary keys does not gurantee that either is
	# unique by itself

	def __repr__(self):
		return '<Hashtag>'

class HashtagSchema(ma.Schema):
	id = fields.Integer()
	hashtag = fields.String()

	def __repr__(self):
		return '<HashtagSchema>'