import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

# TODO: this makes no sense, I think we should be initializing one db object with all the models
# TODO: figure out good way for model discovery and loading for Milestone 3
db = SQLAlchemy()

class Location(db.Model):
	pid = db.Column(db.Integer)
	hashtag = db.Column(db.String(30))

	def __repr__(self):
		return '<Location>'