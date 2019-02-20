from flask import Flask
from config import Config

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    from app import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from models.user import db
    db.init_app(app)

    return app

if __name__ == "__main__":
    app = create_app(Config)
    app.run(host="0.0.0.0", port=5000, debug=True)