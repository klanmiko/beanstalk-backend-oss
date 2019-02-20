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
  def get(self, id):
    pass
  def put(self, id):
    pass
  def post(self):
    auth_token = request.headers.get('Authorization')
    current_app.logger.debug("auth_token: %s", auth_token)

    if not auth_token:
      return {'message': 'No Authorization token'}, 401

    resp = User.decode_auth_token(auth_token)
    if isinstance(resp, str):
      response = {
        'status': 'fail',
        'message': resp
      }
      return response, 401
    auth_user = User.query.filter_by(id=resp).first()
    
    data = request.form
    if not data:
      return {'message', 'No input data provided'}, 400

    if not data['caption']:
      return {'message', 'No caption provided'}, 401

    if not request.files['image']:
      return {'message', 'No image provided'}, 401

    post = Post(uid=auth_user.id, time_posted=datetime.datetime.now(), caption=data['caption'], photo=request.files['image'].read())
    Post.add(post)
    try:
      db.session.flush()
    except Exception as e:
      print(e)
      return {'status': 'failure'}, 500

    #TODO add hashtag and location stuff
    response = PostSchema.dump(post).data
    return response, 200

  def delete(self, id):
    auth_token = request.headers.get('Authorization')
    current_app.logger.debug("auth_token: %s", auth_token)

    if not auth_token:
      return {'message': 'No Authorization token'}, 401

    resp = User.decode_auth_token(auth_token)
    if isinstance(resp, str):
      response = {
        'status': 'fail',
        'message': resp
      }
      return response, 401
    auth_user = User.query.filter_by(id=resp).first()

    post = Post.query.filter(id=id).first()
    if post.uid != auth_user.id:
      return {'message': 'you did not author this post'}, 403
    
    Post.delete().filter(Post.pid==id)
    try:
      db.session.commit()
    except Exception as e:
      print(e)
      return {'status': 'failure'}, 500
    
    return '', 200

class PostCommentsResource(Resource):
  def post(self, id):
    auth_token = request.headers.get('Authorization')
    current_app.logger.debug("auth_token: %s", auth_token)

    if not auth_token:
      return {'message': 'No Authorization token'}, 401

    resp = User.decode_auth_token(auth_token)
    if isinstance(resp, str):
      response = {
        'status': 'fail',
        'message': resp
      }
      return response, 401
    auth_user = User.query.filter_by(id=resp).first()

    post = Post.query.filter(id=id).first()

    json_data = request.get_json(force=True)
    if not json_data:
      return {'message', 'No input data provided'}, 400

    data, errors = owner_user_schema.load(json_data)
    if errors:
      return errors, 422
    
    if not data['comment']:
      return {'message': 'No comment provided'}, 401

    comment = Comment(pid=post.id, uid=auth_user.id, comment=data['comment'], timestamp=datetime.datetime.now())
    Comment.add(comment)

    try:
      db.session.commit()

    except Exception as e:
      print(e)
      return {'status': 'failure', 'message': 'incorrect post id'}, 401

    return '', 200
  
  def get(self, id):
    pass