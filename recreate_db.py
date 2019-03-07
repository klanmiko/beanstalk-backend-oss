import datetime
from flask_sqlalchemy import SQLAlchemy
from models.shared import db
from models.hashtag import Hashtag
from models.post_hashtag import PostHashtag
from models.location import Location
import app

with app.app.app_context():
	# try:
	# 	PostHashtag.__table__.drop(app.db.engine)
	# 	app.db.session.commit()
	# except:
	# 	pass
	# try:
	# 	Hashtag.__table__.drop(app.db.engine)
	# 	app.db.session.commit()
	# except:
	# 	pass

	try:
		Location.__table__.drop(app.db.engine)
		app.db.session.commit()
	except:
		pass

	app.db.create_all()
	app.db.session.commit()