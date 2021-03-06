import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

ma = Marshmallow()

class PostHashtag(db.Model):
	post_id = db.Column(db.ForeignKey('post.pid'), primary_key=True)
	hashtag_id = db.Column(db.ForeignKey('hashtag.id'), primary_key=True)

	def __repr__(self):
		return '<Hashtag>'

class PostHashtagSchema(ma.Schema):
	post_id = fields.Integer()
	hashtag_id = fields.Integer()

	def __repr__(self):
		return '<PostHashtagSchema>'