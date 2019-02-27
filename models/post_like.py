import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

ma = Marshmallow()

class PostLike(db.Model):
	pid = db.Column(db.ForeignKey("post.pid"), nullable=False, primary_key=True, ondelete="CASCADE")
	uid = db.Column(db.ForeignKey("user.id"), nullable=False,  primary_key=True, ondelete="CASCADE")
	timestamp = db.Column(db.DateTime)

	def __repr__(self):
		return '<PostLike>'

class PostLikeSchema(ma.Schema):
	pid = fields.Integer()
	uid = fields.Integer()
	timestamp = fields.DateTime()

	def __repr__(self):
		return '<PostLike>'