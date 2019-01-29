from flask import request, current_app
from flask_restful import Resource
from Model import db, User, UserSchema

users_schema = UserSchema(many=True)
user_schema = UserSchema()

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
			return {'message': 'Missing field(s)'}, 400

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