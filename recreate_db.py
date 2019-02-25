import datetime
from flask_sqlalchemy import SQLAlchemy
from models.shared import db
from models.post import Post
from models.post_like import PostLike
from models.comment import Comment
from models.comment_like import CommentLike

from app import app

with app.app_context():
	db.init_app(app)
#db.drop_all()
	db.create_all()

	# post = Post(uid=2, time_posted=datetime.datetime.now(), caption="this is a caption", photo=b"asdadsasdasd")
	# db.session.add(post)
	db.session.commit()