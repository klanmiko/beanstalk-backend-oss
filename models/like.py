import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

# TODO: this makes no sense, I think we should be initializing one db object with all the models
# TODO: figure out good way for model discovery and loading for Milestone 3
db = SQLAlchemy()

class Like(db.Model):
	pid = db.Column(db.Integer)
	uid = db.Column(db.Integer)
	timestamp = db.Column(db.DateTime)

	def __repr__(self):
		return '<Like>'