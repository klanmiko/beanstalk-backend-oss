import app
from models.notification import Notification

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
		Notification.__table__.drop(app.db.engine)
		app.db.session.commit()
	except:
		pass

	app.db.create_all()
	app.db.session.commit()