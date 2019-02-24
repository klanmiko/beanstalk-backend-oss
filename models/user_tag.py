import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

class UserTag(db.Model):
	pid = db.Column(db.Integer, primary_key=True)
	uid = db.Column(db.Integer, primary_key=True)

	def __repr__(self):
		return '<TaggedPhoto>'