import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	pid = db.Column(db.ForeignKey('post.pid'), unique=True, nullable=False)
	gps = db.Column(db.Integer)
	city = db.Column(db.String(30))
	country = db.Column(db.String(30))

	def __repr__(self):
		return '<Location>'