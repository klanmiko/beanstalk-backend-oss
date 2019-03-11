import datetime
import base64
from collections import OrderedDict

from flask import request, current_app
from flask_restful import Resource
from sqlalchemy.sql.functions import func
from models.location import Location, LocationSchema
from models.user import User, PublicUserSchema
from models.post import Post, PostSchema
from models.post_like import PostLike, PostLikeSchema
from models.follow import Follow
from resources.util import mapPost

from models.shared import db

public_user_schema = PublicUserSchema()
post_schema = PostSchema()
location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)

class LocationResource(Resource):
	# get info on locations
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
		elif "id" in args:
			query = args["id"]

			location = Location.query.filter_by(id=query).first()
			if not location:
				return {'message': 'Location does not exist'}, 400

			posts = db.session.query(Post).filter_by(lid=location.id).order_by(Post.time_posted.desc()).all()
			if posts:
				try:
					posts = list(map(mapPost, posts))
				except Exception as e:
					posts = [mapPost(posts)]

			return {'status': 'success', 'data': posts}, 200

		locations = Location.query.all()
		response = locations_schema.dump(locations).data
		for location in response:
			location['latitude'] = str(location['latitude'])
			location['longitude'] = str(location['longitude'])

		return {'status': 'success', 'data': response}, 200
