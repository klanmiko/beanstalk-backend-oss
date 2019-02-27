import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

ma = Marshmallow()

class Comment(db.Model):
	comment_id = db.Column(db.Integer, primary_key=True)
	pid = db.Column(db.ForeignKey("post.pid"), nullable=False)
	uid = db.Column(db.ForeignKey("user.id"), nullable=False)
	comment = db.Column(db.String(300))
	timestamp = db.Column(db.DateTime, index=True)

	def __repr__(self):
		return '<Comment>'

class CommentSchema(ma.Schema):
	comment_id = fields.Integer()
	pid = fields.Integer()
	uid = fields.Integer()
	comment = fields.String(required=True)
	timestamp = fields.DateTime()

	def __repr__(self):
		return '<Comment>'