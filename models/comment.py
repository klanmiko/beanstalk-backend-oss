import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

class Comment(db.Model):
	comment_id = db.Column(db.Integer, primary_key=True)
	pid = db.Column(db.ForeignKey("post.id"), nullable=False)
	uid = db.Column(db.ForeignKey("user.id"), nullable=False)
	comment = db.Column(db.String(300))
	timestamp = db.Column(db.DateTime)

	def __repr__(self):
		return '<Comment>'