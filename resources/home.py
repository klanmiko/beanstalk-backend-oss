import datetime
import base64
from collections import OrderedDict

from sqlalchemy.sql.functions import func
from flask import request, current_app
from flask_restful import Resource
from models.location import Location
from models.hashtag import Hashtag
from models.user import User, PublicUserSchema
from models.post import Post, PostSchema
from models.post_like import PostLike, PostLikeSchema
from models.follow import Follow

from resources.util import mapPost

from models.shared import db

public_user_schema = PublicUserSchema()
post_schema = PostSchema()

class FollowingPosts(Resource):
  def get(self):
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
    if not auth_user:
      return {'message': 'Auth token does not correspond to existing user'}, 400

    posts = db.session.query(Post, func.count(PostLike.uid), User) \
    .join(User, User.id == Post.uid) \
    .outerjoin(PostLike, PostLike.pid == Post.pid) \
    .join(Follow, Follow.follower_uid == auth_user.id, Follow.following_uid == User.id) \
    .group_by(Post, User) \
    .all()

    def count_likes(tuple):
      post = mapPost(tuple[0])
      like = tuple[1]
      user = tuple[2]
      post['num_likes'] = like
      post['user'] = public_user_schema.dump(user).data
      return post

    if posts:
      posts = list(map(count_likes, posts))

    print(len(posts))

    return {'status': 'success', 'data': posts}, 200
      