from flask import Blueprint, Flask
from config import Config
from flask_restful import Api
from resources.hello_world import HelloWorld
from resources.demo import Demo
from resources.user import *
from resources.post import *
from resources.home import *
from resources.photos import photos

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Routes
api.add_resource(HelloWorld, '/')
api.add_resource(Demo, '/demo')

api.add_resource(UserResource, '/User')
api.add_resource(UserRegisterResource, '/User/register')
api.add_resource(UserLoginResource, '/User/login')
api.add_resource(UserProfileResource, '/User/profile/<username>')
api.add_resource(UserFollowResource, '/User/follow/<username>')

api.add_resource(PostResource, '/Post')
api.add_resource(PostItemResource, '/Post/<pid>')
api.add_resource(PostLikeResource, '/Post/<pid>/like')

api.add_resource(PostItemCommentResource, '/Post/<pid>/comment')
api.add_resource(PostItemCommentItemResource, '/Post/<pid>/comment/<comment_id>')

api.add_resource(FollowingPosts, '/User/Home')
api.add_resource(UserSearchResource, '/User/search')

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(photos, url_prefix='/api/photos')

from models.shared import db
db.init_app(app)