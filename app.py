from flask import Blueprint
from flask_restful import Api
from resources.hello_world import HelloWorld
from resources.demo import Demo
from resources.user import UserResource

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Routes
api.add_resource(HelloWorld, '/')
api.add_resource(Demo, '/demo')
api.add_resource(UserResource, '/User')