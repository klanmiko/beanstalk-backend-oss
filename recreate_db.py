import datetime
from flask_sqlalchemy import SQLAlchemy
from models.shared import db
from models.hashtag import Hashtag
from models.post_hashtag import PostHashtag
import app

with app.app.app_context():
	try:
		PostHashtag.__table__.drop(app.db.engine)
		app.db.session.commit()
	except:
		pass
	try:
		Hashtag.__table__.drop(app.db.engine)
		app.db.session.commit()
	except:
		pass
	app.db.create_all()

	# post = Post(uid=2, time_posted=datetime.datetime.now(), caption="this is a caption", photo=b"asdadsasdasd")
	# db.session.add(post)
	app.db.session.commit()