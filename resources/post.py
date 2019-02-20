import datetime
from flask import request, current_app
from flask_restful import Resource
from models.post import *
from models.location import Location
from models.hashtag import Hashtag
from models.user import User
from models.like import Like
from models.comment import Comment
from models.comment_like import CommentLike

class PostResource(Resource):
  def get():
    pass
  def put():
    pass
  def post():
    pass
  def delete():
    pass

class PostCommentsResource(Resource):
  def post():
    pass
  def get():
    pass