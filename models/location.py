import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

ma = Marshmallow()

# TODO: should we not denormalize and put the lat and long into the posts table?
class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	pid = db.Column(db.ForeignKey('post.pid', ondelete="CASCADE"), unique=True, nullable=False)
	latitude = db.Column(db.Numeric(10, 8), nullable=False)
	longitude = db.Column(db.Numeric(11, 8), nullable=False)
	# gps = db.Column(db.Integer)
	# city = db.Column(db.String(30))
	# country = db.Column(db.String(30))

	def __repr__(self):
		return '<Location>'

class LocationSchema(ma.Schema):
	id = fields.Integer()
	pid = fields.Integer()
	latitude = fields.Decimal()
	longitude = fields.Decimal()

	def __repr__(self):
		return '<LocationSchema>'