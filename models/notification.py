import datetime
from flask import Flask, current_app
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from models.shared import db

ma = Marshmallow()

class Notification(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	uid = db.Column(db.ForeignKey('user.id', ondelete="SET NULL"))
	message = db.Column(db.String(300), nullable=False)
	notif_type = db.Column(db.String(1), nullable=False)
	link = db.Column(db.String(64), nullable=False)
	timestamp = db.Column(db.DateTime, nullable=False)

class NotificationSchema(ma.Schema):
	id = fields.Integer()
	uid = fields.Integer()
	message = fields.String()
	notif_type = fields.String()
	link = fields.String()
	timestamp = fields.DateTime()