import datetime
import base64
import os
from decimal import *
from uuid import UUID, uuid4
from timeit import default_timer as timer
from collections import OrderedDict

from sqlalchemy.sql.functions import func
from flask import request, current_app
from flask_restful import Resource
from models.location import Location, LocationSchema
from models.hashtag import Hashtag
from models.post_hashtag import PostHashtag
from models.user import User, PublicUserSchema, SearchUserSchema
from models.post import Post, PostSchema
from models.post_like import PostLike, PostLikeSchema
from models.comment import Comment, CommentSchema
from models.comment_like import CommentLike, CommentLikeSchema
from models.notification import Notification, NotificationSchema
from models.shared import db

from resources.util import mapPost, mapBinaryImage
from resources.photos import photo_dir

posts_schema = PostSchema(many=True)
post_schema = PostSchema()
post_likes_schema = PostLikeSchema(many=True)
post_like_schema = PostLikeSchema()
comments_schema = CommentSchema(many=True)
comment_schema = CommentSchema()
comment_likes_schema = CommentLikeSchema(many=True)
comment_like_schema = CommentLikeSchema()
search_user_schema = SearchUserSchema()
public_user_schema = PublicUserSchema()
location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)

class PostResource(Resource):
	# get all posts by all users (DONE)
	def get(self):
		start = timer()
		time_elapsed = OrderedDict()
		posts = Post.query.all()
		time_elapsed["time elapsed checkpoint 1"] = timer() - start
		current_app.logger.debug("time elapsed 1: %s", time_elapsed["time elapsed checkpoint 1"])
		posts = posts_schema.dump(posts).data
		time_elapsed["time elapsed checkpoint 2"] = timer() - start
		current_app.logger.debug("time elapsed 2: %s", time_elapsed["time elapsed checkpoint 2"])

		for post in posts:
			post["photo"] = time_elapsed

		return {'status': 'success', 'data': posts}, 200

	# create new post for auth user (DONE)
	def post(self):
		start = timer()
		time_elapsed = OrderedDict()
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
			return {'message': 'User does not exist'}, 400

		data = request.form
		# if not data:
		# 	return {'message': 'No input data provided'}, 400

		if not data.get('caption'):
			return {'message': 'No caption provided'}, 401

		if not request.files.get('image'):
			return {'message': 'No image provided'}, 401

		time_elapsed["time elapsed checkpoint 1"] = timer() - start
		current_app.logger.debug("time elapsed 1: %s", time_elapsed["time elapsed checkpoint 1"])

		photo = request.files.get('image')

		photo_uid = uuid4()
		photo_path = os.path.join(photo_dir, str(photo_uid))

		try:
			photo.save(photo_path)
		except Exception as e:
			print(e)
			return {'message': 'unable to save image'}, 500

		post = Post(uid=auth_user.id, time_posted=datetime.datetime.now(), caption=data['caption'], photo=photo_uid.bytes)

		time_elapsed["time elapsed checkpoint 2"] = timer() - start
		current_app.logger.debug("time elapsed 2: %s", time_elapsed["time elapsed checkpoint 2"])

		#Post.add(post)
		try:
			db.session.add(post)
			db.session.flush()
			time_elapsed["time elapsed checkpoint 3"] = timer() - start
			current_app.logger.debug("time elapsed 3: %s", time_elapsed["time elapsed checkpoint 3"])

			hashtags = data.get("hashtags")
			if not hashtags:
				return {'message': 'No hashtag(s) provided'}, 401

			hashtags = "# " + hashtags.lower() # prepend '#' or else might mistake the first word as a hashtag
			hashtags = ['#' + hashtag.split(" ")[0] for hashtag in hashtags.split("#") if hashtag.split(" ")[0]]
			all_hashtags = []
			for hashtag in hashtags:
				existing_hashtag = Hashtag.query.filter_by(hashtag=hashtag).first()
				if not existing_hashtag:
					existing_hashtag = Hashtag(hashtag=hashtag)
					db.session.add(existing_hashtag)
					db.session.commit()

				new_post_hashtag = PostHashtag(post_id=post.pid, hashtag_id=existing_hashtag.id)
				db.session.add(new_post_hashtag)
			hashtags = (" ").join(hashtags)
			post.hashtags = hashtags

			place_name = data.get("placeName")
			latitude = data.get("lat")
			longitude = data.get("long")
			if not (place_name and latitude and longitude):
				return {'message': 'No location provided or location info incomplete'}, 401

			try:
				existing_location = Location.query.filter_by(place_name=place_name).first()
				if not existing_location:
					latitude = Decimal(latitude)
					longitude = Decimal(longitude)
					existing_location = Location(place_name=place_name, latitude=latitude, longitude=longitude)
					db.session.add(existing_location)
					db.session.flush()
				post.lid = existing_location.id
			except Exception as e:
				return {'message': str(e)}, 401

			db.session.commit()
		except Exception as e:
			print(e)
			db.session.rollback()
			return {'status': 'failure'}, 500

		#TODO add hashtag and location stuff
		response = post_schema.dump(post).data
		response['photo'] = str(UUID(bytes=response['photo']))

		return response, 201

	# delete all posts by all users (DONE)
	def delete(self):
	    num_rows_deleted = db.session.query(Post).delete()
	    db.session.commit()
	    result = {"num_rows_deleted": num_rows_deleted}
	    return {'status': 'success', 'data': result}, 201

class PostLikeResource(Resource):
	# like a post (DONE)
	def post(self, pid):
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

		post = Post.query.filter_by(pid=pid).first()
		if not post:
			return {'message': 'Post does not exist'}, 400

		try:
			timestamp = datetime.datetime.utcnow()
			post_like = PostLike(pid=pid, uid=auth_user.id, timestamp=timestamp)
			db.session.add(post_like)
			db.session.flush()

			notification = Notification(uid=post.uid, message="{username} liked your post.".format(username=auth_user.username),
										notif_type="L", link=pid, timestamp=timestamp)
			db.session.add(notification)
			db.session.commit()

		except Exception:
			return {'message': 'User already liked post'}, 400

		return {'status': 'success'}, 200

	# unlike (TODO: implementation)
	def delete(self, pid):
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

		status = db.session.query(PostLike).filter(PostLike.pid==pid, PostLike.uid==auth_user.id).delete()
		if status == 0:
			return {'status': 'failure', 'message': "can't unlike"}, 401

		try:
			db.session.commit()
		except Exception as e:
			print(e)
			db.session.rollback()
			return {'status': 'failure'}, 500

		return '', 200

class PostItemResource(Resource):
	# get post info, comments and likes for a specific post (DONE)
	def get(self, pid):
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

		like_exists = db.session.query(PostLike).join(Post, Post.pid==PostLike.pid).filter(PostLike.uid == auth_user.id).subquery()

		(post, likes, user, is_liked, location) = db.session.query(Post, func.count(PostLike.uid), User, like_exists.c.pid, Location) \
		.outerjoin(PostLike, PostLike.pid == Post.pid) \
		.outerjoin(Location, Location.id == Post.lid) \
		.join(User, User.id == Post.uid) \
		.outerjoin(like_exists, like_exists.c.pid == Post.pid) \
		.filter(Post.pid==pid) \
		.group_by(Post, User, like_exists.c.pid, Location) \
		.first()

		if not post:
			return {'message': 'Post does not exist'}, 400

		result = mapPost(post)
		result["num_likes"] = likes

		result["user"] = public_user_schema.dump(user).data
		try:
			result['user']['profile_pic'] = mapBinaryImage(result['user']['profile_pic'])
		except Exception as e:
			print(e)

		result["like"] = True if is_liked is not None else False

		if location:
			result['location'] = location_schema.dump(location).data
			result['location']['latitude'] = str(result['location']['latitude'])
			result['location']['longitude'] = str(result['location']['longitude'])

		r = db.session.query(Comment, func.count(CommentLike.uid), User.username) \
		.join(User, User.id == Comment.uid) \
		.outerjoin(CommentLike, CommentLike.comment_id == Comment.comment_id) \
		.filter(Comment.pid==post.pid) \
		.group_by(Comment, User.username) \
		.order_by(Comment.timestamp.asc()) \
		.all()

		try:
			(comments, comment_likes, users) = zip(*r)

			result['comments'] = comments_schema.dump(comments).data

			for comment, like, user in zip(result['comments'], comment_likes, users):
				comment['num_likes'] = like
				comment['user'] = user
			# (post, comments, likes) = db.session.query(Post, Comment, Like).filter(Post.pid==id).outerjoin(Comment, Comment.pid == Post.pid).outerjoin(Like, Like.pid == Post.pid).first()
		except Exception:
			# probably doesn't have comments
			pass
		
		return result, 200

	# update the post's caption (DONE)
	def put(self, pid):
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

		post = Post.query.filter_by(pid=pid).first()
		if not post:
			return {'message': 'Post does not exist'}, 400

		if post.uid != auth_user.id:
			return {'message': 'User does not have permission to update this post'}, 403

		data, errors = post_schema.load(request.get_json(force=True))
		if errors:
			return errors, 422

		if 'caption' not in data:
			return {'message': 'Missing caption field'}, 400

		post.caption = data['caption']
		db.session.commit()

		result = post_schema.dump(post).data
		result['photo'] = "Empty for testing so it doesn't lag"

		return {'status': 'success', 'data': result}, 201

	# delete the post (TODO: implementation)
	def delete(self, pid):
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

		try:
			db.session.query(Post).filter(Post.pid==pid, Post.uid==auth_user.id).delete()

			db.session.commit()

			return '', 200
		except Exception:
			return {'status': 'failure', 'message': 'either post does not exist or you do not have permissions'}, 403

		return '', 200

class PostItemCommentResource(Resource):
	# get all comments for a post (DONE)
	def get(self, pid):
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

		comments = Comment.query.filter_by(pid=pid).order_by(Comment.timestamp.asc()).all()
		comments = comments_schema.dump(comments).data

		for comment in comments:
			comment['num_likes'] = len(CommentLike.query.filter_by(comment_id=comment['comment_id']).all())

		return {'status': 'success', 'data': comments}, 200

	# create a new comment for a specific post (DONE)
	def post(self, pid):
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

		post = Post.query.filter_by(pid=pid).first()
		if not post:
			return {'message': 'Post does not exist'}, 400

		json_data = request.get_json(force=True)
		if not json_data:
			return {'message', 'No input data provided'}, 400

		data, errors = comment_schema.load(json_data)
		if errors:
			return errors, 422

		timestamp = datetime.datetime.utcnow()

		comment = Comment(pid=post.pid, uid=auth_user.id, comment=data['comment'], timestamp=timestamp)
		db.session.add(comment)
		db.session.flush()

		notification = Notification(uid=post.uid, message="{username} commented on your post.".format(username=auth_user.username),
									notif_type="C", link=pid, timestamp=timestamp)
		db.session.add(notification)
		db.session.commit()

		#TODO add hashtag and location stuff
		response = comment_schema.dump(comment).data
		response['user'] = auth_user.username

		return {'status': 'success', 'data': response}, 201

	# delete all comments for a specific post (TODO: implementation)
	def delete(self, pid):
		pass

class PostItemCommentItemResource(Resource):
	# get comment info and number of likes for comment (DONE)
	def get(self, pid, comment_id):
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

		post = Post.query.filter_by(pid=pid).first()
		if not post:
			return {'message': 'Post does not exist'}, 400

		comment = Comment.query.filter_by(comment_id=comment_id).first()
		if not comment:
			return {'message': 'Comment does not exist'}, 400

		result = comment_schema.dump(comment).data
		result["num_likes"] = len(CommentLike.query.filter_by(comment_id=comment.comment_id).all())

		# TODO actually encode this response
		return result, 200

	# like a comment (DONE)
	def post(self, pid, comment_id):
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

		post = Post.query.filter_by(pid=pid).first()
		if not post:
			return {'message': 'Post does not exist'}, 400

		comment = Comment.query.filter_by(comment_id=comment_id).first()
		if not comment:
			return {'message': 'Comment does not exist'}, 400

		data, errors = comment_like_schema.load(request.get_json(force=True))
		if errors:
			return errors, 422

		if CommentLike.query.filter_by(comment_id=comment_id, uid=auth_user.id).first():
			return {'message': 'User already liked comment'}, 400

		comment_like = CommentLike(comment_id=comment_id, uid=auth_user.id, timestamp=datetime.datetime.utcnow())
		db.session.add(comment_like)
		db.session.commit()

		result = comment_like_schema.dump(post).data

		return {'status': 'success', 'data': result}, 201

	# update a comment (DONE)
	def put(self, pid, comment_id):
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

		post = Post.query.filter_by(pid=pid).first()
		if not post:
			return {'message': 'Post does not exist'}, 400

		comment = Comment.query.filter_by(comment_id=comment_id).first()
		if not comment:
			return {'message': 'Comment does not exist'}, 400

		if comment.uid != auth_user.id:
			return {'message': 'User does not have permission to update this comment'}, 403

		data, errors = comment_schema.load(request.get_json(force=True))
		if errors:
			return errors, 422

		if 'comment' not in data:
			return {'message': 'Missing comment field'}, 400

		comment.comment = data['comment']
		db.session.commit()

		result = comment_schema.dump(comment).data

		return {'status': 'success', 'data': result}, 201

	# delete a comment (TODO: implementation)
	def delete(self, pid, comment_id):
		pass

class PostLocationResource(Resource):
	def get(self, pid):
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

		location = Location.query.filter_by(pid=pid).first()
		location = location_schema.dump(location).data
		if location:
			location["latitude"] = str(location["latitude"])
			location["longitude"] = str(location["longitude"])

		return {'status': 'success', 'data': location}, 200