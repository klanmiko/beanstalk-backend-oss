import datetime
import base64
from collections import OrderedDict

from flask import request, current_app
from flask_restful import Resource
from models.hashtag import Hashtag, HashtagSchema
from models.post_hashtag import PostHashtag, PostHashtagSchema
from sqlalchemy.sql.functions import func
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
hashtag_schema = HashtagSchema()
hashtags_schema = HashtagSchema(many=True)
post_hashtag_schema = PostHashtagSchema()
post_hashtags_schema = PostHashtagSchema(many=True)

class HashtagResource(Resource):
	# get info on hashtags
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

		args = request.args

		if "username" in args:
			pass
		elif "pid" in args:
			pass
		elif "hashtag" in args:
			query = str(args["hashtag"])

			hashtag = Hashtag.query.filter_by(hashtag="#"+query).first()
			if not hashtag:
				return {'message': 'Hashtag does not exist'}, 400

			# adapting Klan's home query cuz idk what's going on
			# removed join with follow table and added join with posthashtag table
			# TODO: should we prioritize posts with hashtags from followers first?
			posts = db.session.query(Post).join(PostHashtag, (PostHashtag.hashtag_id == hashtag.id) & (PostHashtag.post_id == Post.pid)).order_by(Post.time_posted.desc()).all()

			# If we display like a feed similar to home page, then we need to do the below query:
			# like_exists = db.session.query(PostLike).join(Post, Post.pid==PostLike.pid).filter(PostLike.uid == auth_user.id).subquery()
			# posts = db.session.query(Post, func.count(PostLike.uid), User.username, like_exists.c.pid) \
			# .join(User, User.id == Post.uid) \
			# .outerjoin(PostLike, PostLike.pid == Post.pid) \
			# .join(PostHashtag, (PostHashtag.hashtag_id == hashtag.id) & (PostHashtag.post_id == Post.pid)) \
			# .outerjoin(like_exists, like_exists.c.pid==Post.pid) \
			# .group_by(Post, User.username, like_exists.c.pid) \
			# .order_by(Post.time_posted.desc()) \
			# .all()

			# def count_likes(tuple):
			# 	post = mapPost(tuple[0])
			# 	like = tuple[1]
			# 	user = tuple[2]
			# 	post['num_likes'] = like
			# 	post['user'] = user
			# 	post['like'] = True if tuple[3] is not None else False
			#  	return post

			if posts:
				try:
					posts = list(map(mapPost, posts))
				except Exception as e:
					posts = [mapPost(posts)]
				#posts = list(map(count_likes, posts))

			return {'status': 'success', 'data': posts}, 200

		all_hashtags = Hashtag.query.all()
		all_hashtags = hashtags_schema.dump(all_hashtags).data

		all_post_hashtags = PostHashtag.query.all()
		all_post_hashtags = post_hashtags_schema.dump(all_post_hashtags).data

		response = {
			"hashtags": all_hashtags,
			"post_hashtags": all_post_hashtags
		}

		return {'status': 'success', 'data': response}, 200
