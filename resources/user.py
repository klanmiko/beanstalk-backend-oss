from flask import request, current_app
from flask_restful import Resource
from Model import *

users_schema = UserSchema(many=True)
user_schema = UserSchema()
user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()
owner_user_schema = OwnerUserSchema()
private_user_schema = PrivateUserSchema()
public_user_schema = PublicUserSchema()

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
		json_data = request.get_json(force=True)
		if not json_data:
			return {'message': 'No input data provided'}, 400

		data, errors = user_register_schema.load(json_data)
		if errors:
			return errors, 422

		# check how this works in docs
		# what if I want to filter by both username and email?
		existing_user = User.query.filter_by(username=data['username']).first()
		if existing_user:
			return {'message': 'User already exists'}, 400

		if 'username' not in data or 'email' not in data:
			return {'message': 'User Register - missing field(s)'}, 400

		user = User(
			username=data['username'],
			email=data['email']
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
		response = {
			'status': 'success',
			'message': 'Successfully logged in.',
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

		if user.username == auth_user.username: # viewing your own profile
			result = owner_user_schema.dump(user).data
		else: # viewing someone else's profile
			result = private_user_schema.dump(user).data
		return {'status': 'success', 'data': result}, 200

	def put(self, username):
		auth_token = request.headers.get('Authorization')
		current_app.logger.debug("auth_token: %s", auth_token)

		if not auth_token:
			return {'message': 'No Authorization token'}, 401

		json_data = request.get_json(force=True)
		if not json_data:
			return {'message', 'No input data provided'}, 400

		data, errors = owner_user_schema.load(json_data)
		if errors:
			return errors, 422

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

		if user.username == auth_user.username:
			updatable_fields = ["first_name", "last_name", "privacy"]
			for field in data:
				if field in updatable_fields:
					setattr(user, field, data[field])
				else:
					return {'message': 'No permission to update {}'.format(field)}, 401
			db.session.commit()
			result = owner_user_schema.dump(user).data
		else:
			return {'message': 'No permission to update user profile for other users'}, 401

		return {'status': 'success', 'data': result}, 204



