from flask import request, current_app
from flask_restful import Resource
from models.hashtag import Hashtag, HashtagSchema
from models.post_hashtag import PostHashtag, PostHashtagSchema
from models.shared import db

hashtag_schema = HashtagSchema()
hashtags_schema = HashtagSchema(many=True)
post_hashtag_schema = PostHashtagSchema()
post_hashtags_schema = PostHashtagSchema(many=True)

class HashtagResource(Resource):
	# get info on hashtags
	def get(self):
		args = request.args

		if "username" in args:
			pass
		elif "pid" in args:
			pass
		elif "hashtag" in args:
			pass

		all_hashtags = Hashtag.query.all()
		all_hashtags = hashtags_schema.dump(all_hashtags).data

		all_post_hashtags = PostHashtag.query.all()
		all_post_hashtags = post_hashtags_schema.dump(all_post_hashtags).data

		response = {
			"hashtags": all_hashtags,
			"post_hashtags": all_post_hashtags
		}

		return {'status': 'success', 'data': response}, 200
