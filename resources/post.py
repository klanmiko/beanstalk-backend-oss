import datetime
import base64
from timeit import default_timer as timer
from collections import OrderedDict

from flask import request, current_app
from flask_restful import Resource
from models.post import *
from models.location import Location
from models.hashtag import Hashtag
from models.user import User
from models.like import Like
from models.comment import Comment
from models.comment_like import CommentLike

posts_schema = PostSchema(many=True)
post_schema = PostSchema()

class PostResource(Resource):
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

		try:
			db.session.commit()
		except Exception as e:
			print(e)
			db.session.rollback()
			return {'status': 'failure'}, 500

		response["photo"] = str(response["photo"])

		return response, 200

	def delete(self):
	    num_rows_deleted = db.session.query(Post).delete()
	    db.session.commit()
	    result = {"num_rows_deleted": num_rows_deleted}
	    return {'status': 'success', 'data': result}, 201

class PostItemResource(Resource):
	def get(self, id):
		pass

	def put(self, id):
		pass

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