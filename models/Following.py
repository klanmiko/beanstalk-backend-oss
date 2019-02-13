import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Following(db.Model):
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False, primary_key=True)
    following_id = db.Column(db.ForeignKey("user.id"), nullable=False, primary_key=True)

class FollowingAggregation(db.Model):
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False, primary_key=True)
    followers = db.Column(db.Integer, db.CheckConstraint('followers>=0'), default=0, nullable=False)
    following = db.Column(db.Integer, db.CheckConstraint('followers>=0'), default=0, nullable=False)