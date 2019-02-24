import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

class Follow(db.Model):
	follower_uid = db.Column(db.ForeignKey("user.id"), nullable=False, primary_key=True)
	following_uid = db.Column(db.ForeignKey("user.id"), nullable=False, primary_key=True)
	timestamp = db.Column(db.DateTime)
	request = db.Column(db.Integer)

class FollowingAggregation(db.Model):
	user_id = db.Column(db.ForeignKey("user.id"), nullable=False, primary_key=True)
	followers = db.Column(db.Integer, db.CheckConstraint('followers>=0'), default=0, nullable=False)
	following = db.Column(db.Integer, db.CheckConstraint('followers>=0'), default=0, nullable=False)

	def __repr__(self):
		return '<Follow>'