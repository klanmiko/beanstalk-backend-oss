import json
import datetime
import base64
from flask import request, current_app
from sqlalchemy.sql.functions import func
from flask_restful import Resource, reqparse
from models.shared import db
from models.user import *
from models.follow import *
from models.post import *
from models.hashtag import *
from models.location import *
from models.notification import *
from resources.util import mapPost, mapBinaryImage

users_schema = UserSchema(many=True)
user_schema = UserSchema()
user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()
owner_user_schema = OwnerUserSchema()
private_user_schema = PrivateUserSchema()
public_user_schema = PublicUserSchema()
following_aggregation_schema = FollowingAggregationSchema()
follow_schema = FollowSchema()
search_users_schema = SearchUserSchema(many=True)
hashtag_schema = HashtagSchema()
hashtags_schema = HashtagSchema(many=True)
location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)
notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)

class UserResource(Resource):
	def get(self):
		users = User.query.all()
		users = users_schema.dump(users).data
		return {'status': 'success', 'data': users}, 200

	def post(self):
		json_data = request.get_json(force=True)
		if not json_data:
			return {'message': 'No input data provided'}, 400

		data, errors = user_schema.load(json_data)
		if errors:
			return errors, 422

		# check how this works in docs
		# what if I want to filter by both username and email?
		existing_user = User.query.filter_by(username=data['username']).first()
		if existing_user:
			return {'message': 'User already exists'}, 400

		if 'username' not in data or 'email' not in data:
			return {'message': 'User - missing field(s)'}, 400

		user = User(
			username=data['username'],
			email=data['email']
			)
		db.session.add(user)
		db.session.commit()

		result = user_schema.dump(user).data

		return {'status': 'success', 'data': result}, 201

	def put(self):
		json_data = request.get_json(force=True)
		if not json_data:
			return {'message', 'No input data provided'}, 400

		data, errors = user_schema.load(json_data)
		if errors:
			return errors, 422

		existing_user = User.query.filter_by(id=data['id']).first()
		if not existing_user:
			return {'message': 'User does not exist'}, 400

		# example for printing error logs
		# current_app.logger.debug("type(existing_user): %s", type(existing_user))
		if 'username' in data:
			existing_user.username = data['username']
		if 'email' in data:
			existing_user.email = data['email']
		# we don't need to add again because the entry is already in db?
		# how does the db know that we just updated the user?
		db.session.commit()

		result = user_schema.dump(existing_user).data

		return {'status': 'success', 'data': result}, 204 # 204: No content, return json will might not show

	def delete(self):
		json_data = request.get_json(force=True)
		if not json_data:
			return {'message': 'No input data provided'}, 400

		data, errors = user_schema.load(json_data)
		if errors:
			return errors, 422

		existing_user = User.query.filter_by(id=data['id']).delete()
		db.session.commit()

		result = user_schema.dump(existing_user).data

		return {'status': 'success', 'data': result}, 204

class UserRegisterResource(Resource):
	def post(self):
		try:
			json_data = request.get_json(force=True)
			if not json_data:
				return {'message': 'No input data provided'}, 400

			data, errors = user_register_schema.load(json_data)
			if errors:
				return errors, 422

			current_app.logger.debug("data: %s", json.dumps(data, indent=4))

			# check how this works in docs
			# what if I want to filter by both username and email?
			existing_user = User.query.filter_by(username=data['username']).first()
			if existing_user:
				return {'message': 'User already exists'}, 400

			required_fields = ["username", "email", "password", "first_name", "last_name"]
			for field in required_fields:
				if not data[field]:
					return {'message': 'Fields cannot be empty'}, 400

			user = User(
				username=data['username'],
				email=data['email'],
				first_name=data['first_name'],
				last_name=data['last_name'],
				privacy=False,
				created_at=datetime.datetime.utcnow(),
				updated_at=None,
				profile_pic=None
				)
			user.set_password(data['password'])

			db.session.add(user)
			db.session.commit()

			#result = user_schema.dump(user).data
			auth_token = user.encode_auth_token(user.id)
			response = {
				'status': 'success',
				'message': 'Successfully registered.',
				'auth_token': auth_token.decode()
			}

			return response, 201
		except Exception as e:
			return {'message': str(e)}, 400

class UserLoginResource(Resource):
	def post(self):
		json_data = request.get_json(force=True)
		if not json_data:
			return {'message': 'No input data provided'}, 400

		data, errors = user_login_schema.load(json_data)
		if errors:
			return errors, 422

		# check how this works in docs
		# what if I want to filter by both username and email?
		user = User.query.filter_by(username=data['username']).first()
		if not user:
			return {'message': 'User does not exist'}, 400

		if 'username' not in data or 'password' not in data:
			return {'message': 'User Login - missing field(s)'}, 400

		if not user.check_password(data['password']):
			return {'message': "Wrong password"}, 400

		auth_token = user.encode_auth_token(user.id)
		user = user_login_schema.dump(user).data
		response = {
			'status': 'success',
			'message': 'Successfully logged in.',
			'data': user,
			'auth_token': auth_token.decode()
		}

		return response, 200

class UserProfileResource(Resource):
	# get info about a profile
	def get(self, username):
		auth_token = request.headers.get('Authorization')
		current_app.logger.debug("auth_token: %s", auth_token)

		if not auth_token:
			return {'message': 'No Authorization token'}, 401

		try:
			(user, followers) = db.session.query(User, FollowingAggregation) \
			.filter(User.username==username) \
			.outerjoin(FollowingAggregation, FollowingAggregation.user_id == User.id) \
			.first()

		except Exception:
			return {'message': 'User does not exist'}, 400

		r = db.session.query(Post, Location) \
		.filter(Post.uid == user.id) \
		.outerjoin(Location, Location.id == Post.lid) \
		.order_by(Post.time_posted.desc()) \
		.all()

		posts = []
		locations = []

		try:
			(posts, locations) = zip(*r)

			locations = list(filter(None, locations))

			if posts:
				try:
					posts = list(map(mapPost, posts))
				except Exception as e:
					posts = [mapPost(posts)]
		except:
			pass

		resp = User.decode_auth_token(auth_token)
		if isinstance(resp, str):
			response = {
				'status': 'fail',
				'message': resp
			}
			return response, 401
		auth_user = User.query.filter_by(id=resp).first()
		isFollowing = db.session.query(Follow).filter(Follow.follower_uid == auth_user.id, Follow.following_uid == user.id).first()

		if user.username == auth_user.username: # viewing your own profile
			result = owner_user_schema.dump(user).data
		else: # viewing someone else's profile
			result = private_user_schema.dump(user).data

		if result['profile_pic']:
			result['profile_pic'] = mapBinaryImage(result['profile_pic'])

		if followers:
			followers = following_aggregation_schema.dump(followers).data
		
		return {'status': 'success', 'data': {
			'user': result,
			'followers': followers,
			'isFollowing': follow_schema.dump(isFollowing).data if isFollowing else False,
			'posts': posts,
			'locations': locations_schema.dump(locations).data,
			'num_posts': len(posts)
			}}, 200

	def put(self, username):
		auth_token = request.headers.get('Authorization')
		current_app.logger.debug("auth_token: %s", auth_token)

		if not auth_token:
			return {'message': 'No Authorization token'}, 401

		user = User.query.filter_by(username=username).first()
		if not user:
			return {'message': 'User does not exist'}, 400

		resp = User.decode_auth_token(auth_token)
		if isinstance(resp, str):
			response = {
				'status': 'fail',
				'message': resp
			}
			return response, 401
		auth_user = User.query.filter_by(id=resp).first()

		if user.username != auth_user.username:
			return {'message': 'No permission to update user profile for other users'}, 401

		content_type = request.headers.get('Content-Type')
		if not content_type:
			return {'message': 'No Content-Type header'}, 401

		current_app.logger.debug("content_type: %s", content_type)
		if "multipart/form-data" in content_type:
			if request.files.get('image'):
				user.profile_pic = request.files['image'].read()

			data = request.form
			updatable_fields = ["first_name", "last_name", "privacy", "email"]
			for field in data:
				if field not in updatable_fields:
					continue
				elif data[field]:
					setattr(user, field, data[field])
		else: # backwards compat.
			json_data = request.get_json(force=True)
			if not json_data:
				return {'message', 'No input data provided'}, 400

			data, errors = owner_user_schema.load(json_data)
			if errors:
				return errors, 422

			updatable_fields = ["first_name", "last_name", "privacy", "email"]
			for field in data:
				if field in updatable_fields and data[field]:
					setattr(user, field, data[field])
				elif field in updatable_fields and not data[field]:
					pass
				else:
					return {'message': 'No permission to update {}'.format(field)}, 401
		setattr(user, "updated_at", datetime.datetime.utcnow())
		db.session.commit()
		result = owner_user_schema.dump(user).data
		if result['profile_pic']:
			result['profile_pic'] = mapBinaryImage(result['profile_pic'])

		return {'status': 'success', 'data': result}, 200


class UserFollowResource(Resource):
	def post(self, username):
		auth_token = request.headers.get('Authorization')
		current_app.logger.debug("auth_token: %s", auth_token)

		if not auth_token:
			return {'message': 'No Authorization token'}, 401

		user = User.query.filter_by(username=username).first()
		if not user:
			return {'message': 'User does not exist'}, 400

		resp = User.decode_auth_token(auth_token)
		if isinstance(resp, str):
			response = {
				'status': 'fail',
				'message': resp
			}
			return response, 401
		auth_user = User.query.filter_by(id=resp).first()
		timestamp = datetime.datetime.now()
		followRelationship = Follow(follower_uid=resp, following_uid=user.id, timestamp=timestamp, request=1)
		try:
			db.session.add(followRelationship)
			db.session.flush()

			notification = Notification(uid=user.id, message="{username} followed you.".format(username=auth_user.username),
										notif_type="F", link=auth_user.username, timestamp=timestamp)
			db.session.add(notification)
			db.session.flush()
		except Exception as e:
			print(e)
			db.session.rollback()
			return {'status': 'fail', 'message': 'already following user'}, 401

		aggregation = FollowingAggregation(user_id=auth_user.id, followers=0, following=0)
		try:
			with db.session.begin_nested():
				db.session.add(aggregation)
		except Exception as e:
			print(e)

		db.session.query(FollowingAggregation).filter(FollowingAggregation.user_id == auth_user.id).update({'following': FollowingAggregation.following + 1})

		aggregation = FollowingAggregation(user_id=user.id, followers=0, following=0)

		try:
			with db.session.begin_nested():
				db.session.add(aggregation)
		except Exception as e:
			print(e)

		db.session.query(FollowingAggregation).filter(FollowingAggregation.user_id == user.id).update({'followers': FollowingAggregation.followers + 1})

		try:
			db.session.commit()
		except Exception as e:
			print(e)
			db.session.rollback()
			return {'status': 'failure'}, 500

		return '', 200

	def delete(self, username):
		auth_token = request.headers.get('Authorization')
		current_app.logger.debug("auth_token: %s", auth_token)

		if not auth_token:
			return {'message': 'No Authorization token'}, 401

		user = User.query.filter_by(username=username).first()
		if not user:
			return {'message': 'User does not exist'}, 400

		resp = User.decode_auth_token(auth_token)
		if isinstance(resp, str):
			response = {
				'status': 'fail',
				'message': resp
			}
			return response, 401
		auth_user = User.query.filter_by(id=resp).first()

		try:
			status = db.session.query(Follow).filter(Follow.follower_uid==auth_user.id, Follow.following_uid==user.id).delete()
			if status == 0:
				raise Exception('no rows deleted')
		except Exception as e:
			print(e)
			return {'status': 'fail', 'message': 'not following user'}, 401

		db.session.query(FollowingAggregation).filter(FollowingAggregation.user_id == auth_user.id).update({'following': FollowingAggregation.following - 1})
		db.session.query(FollowingAggregation).filter(FollowingAggregation.user_id == user.id).update({'followers': FollowingAggregation.followers - 1})
		try:
			db.session.commit()
		except Exception as e:
			print(e)
			db.session.rollback()
			return {'status': 'failure'}, 500

		return '', 200

class UserSearchResource(Resource):
	def get(self):
		args = request.args

		if "query" not in args:
			return {'message': 'No query parameter in url'}, 401

		query = str(args['query'])

		users = User.query.filter(User.username.ilike(query + "%")).all()
		users = search_users_schema.dump(users).data

		hashtags = Hashtag.query.filter(Hashtag.hashtag.ilike("#" + query + "%")).all()
		hashtags = hashtags_schema.dump(hashtags).data

		locations = Location.query.filter(Location.place_name.ilike(query + "%")).all()
		locations = locations_schema.dump(locations).data
		for location in locations:
			location["latitude"] = str(location["latitude"])
			location["longitude"] = str(location["longitude"])

		response = users + hashtags + locations

		return {'status': 'success', 'data': response}, 200

class NotificationResource(Resource):
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

		notifications = Notification.query.filter_by(uid=auth_user.id).order_by(Notification.timestamp.desc()).all()
		notifications = notifications_schema.dump(notifications).data

		return {'status': 'success', 'data': notifications}, 200
	
class NotificationItemResource(Resource):
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
		if not auth_user:
			return {'message': 'Auth token does not correspond to existing user'}, 400
		
		try:
			db.session.query(Notification).filter(Notification.id == id, Notification.uid == auth_user.id).update({'read': True})
			db.session.commit()
		except Exception as e:
			return {'message': 'Notification does not correspond with that user'}, 403
		
		return {'status': 'success'}, 200
