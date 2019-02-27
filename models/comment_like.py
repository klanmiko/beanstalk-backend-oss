import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

ma = Marshmallow()

class CommentLike(db.Model):
	comment_id = db.Column(db.ForeignKey("comment.comment_id"), nullable=False, primary_key=True, ondelete="CASCADE")
	uid = db.Column(db.ForeignKey("user.id"), nullable=False, primary_key=True, ondelete="CASCADE")
	timestamp = db.Column(db.DateTime)

	def __repr__(self):
		return '<CommentLike>'

class CommentLikeSchema(ma.Schema):
	comment_id = fields.Integer()
	uid = fields.Integer()
	timestamp = fields.DateTime()

	def __repr__(self):
		return '<CommentLike>'