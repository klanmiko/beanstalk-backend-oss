import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

# TODO: this makes no sense, I think we should be initializing one db object with all the models
# TODO: figure out good way for model discovery and loading for Milestone 3
db = SQLAlchemy()

class Post(db.Model):
	pid = db.Column(db.Integer, primary_key=True)
	uid = db.Column(db.ForeignKey('user.id'), nullable=False)
	time_posted = db.Column(db.DateTime, nullable=False)
	photo = db.Column(db.LargeBinary, nullable=False)
	caption = db.Column(db.String(300), nullable=False)

class PostSchema(ma.Schema):
	pid = fields.Integer()
	uid = fields.Integer()
	photo = db.Column(db.LargeBinary, nullable=False)
	caption = fields.String()

	def __repr__(self):
		return '<Post>'