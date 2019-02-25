import datetime
import base64
from timeit import default_timer as timer
from collections import OrderedDict

from sqlalchemy.sql.functions import func
from flask import request, current_app
from flask_restful import Resource
from models.location import Location
from models.hashtag import Hashtag
from models.user import User
from models.post import Post, PostSchema
from models.post_like import PostLike, PostLikeSchema
from models.comment import Comment, CommentSchema
from models.comment_like import CommentLike, CommentLikeSchema
from models.shared import db

from resources.util import mapPost

posts_schema = PostSchema(many=True)
post_schema = PostSchema()
post_likes_schema = PostLikeSchema(many=True)
post_like_schema = PostLikeSchema()
comments_schema = CommentSchema(many=True)
comment_schema = CommentSchema()
comment_likes_schema = CommentLikeSchema(many=True)
comment_like_schema = CommentLikeSchema()

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
		post = Post(uid=auth_user.id, time_posted=datetime.datetime.now(), caption=data['caption'], photo=(request.files['image'].read()))

		time_elapsed["time elapsed checkpoint 2"] = timer() - start
		current_app.logger.debug("time elapsed 2: %s", time_elapsed["time elapsed checkpoint 2"])
		#Post.add(post)
		try:
			db.session.add(post)
			db.session.commit()
			time_elapsed["time elapsed checkpoint 3"] = timer() - start
			current_app.logger.debug("time elapsed 3: %s", time_elapsed["time elapsed checkpoint 3"])
			#db.session.flush()

		except Exception as e:
			print(e)
			return {'status': 'failure'}, 500

		#TODO add hashtag and location stuff
		response = post_schema.dump(post).data
		response["photo"] = time_elapsed

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

		try:
			post_like = PostLike(pid=pid, uid=auth_user.id, timestamp=datetime.datetime.utcnow())
			db.session.add(post_like)
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

		(post, likes) = db.session.query(Post, func.count(PostLike.uid)) \
		.outerjoin(PostLike, PostLike.pid == Post.pid) \
		.filter(Post.pid==pid) \
		.group_by(Post) \
		.first()

		if not post:
			return {'message': 'Post does not exist'}, 400

		result = mapPost(post)
		result["num_likes"] = likes

		r = db.session.query(Comment, func.count(CommentLike.uid)) \
		.outerjoin(CommentLike, CommentLike.comment_id == Comment.comment_id) \
		.filter(Comment.pid==post.pid) \
		.group_by(Comment) \
		.all()

		try:
			(comments, comment_likes) = zip(*r)

			result['comments'] = comments_schema.dump(comments).data
			
			for comment, like in zip(result['comments'], comment_likes):
				comment['num_likes'] = like
			# (post, comments, likes) = db.session.query(Post, Comment, Like).filter(Post.pid==id).outerjoin(Comment, Comment.pid == Post.pid).outerjoin(Like, Like.pid == Post.pid).first()
		except Exception:
			# probably doesn't have comments
			pass
		# TODO actually encode this response
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

		post = Post.query.filter(pid=pid).first()
		if post.uid != auth_user.id:
			return {'message': 'User does not have permission to delete this post'}, 403

		Post.delete().filter(Post.pid==id)
		try:
			db.session.commit()
		except Exception as e:
			print(e)
			return {'status': 'failure'}, 500

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

		comments = Comment.query.filter_by(pid=pid).all()
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

		comment = Comment(pid=post.pid, uid=auth_user.id, comment=data['comment'], timestamp=datetime.datetime.now())

		db.session.add(comment)
		db.session.commit()

		#TODO add hashtag and location stuff
		response = comment_schema.dump(comment).data

		return response, 201

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