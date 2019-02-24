import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

class CommentLike(db.Model):
	comment_id = db.Column(db.ForeignKey("comment.id"), nullable=False, primary_key=True)
	uid = db.Column(db.ForeignKey("user.id"), nullable=False, primary_key=True)
	timestamp = db.Column(db.DateTime)

	def __repr__(self):
		return '<CommentLike>'