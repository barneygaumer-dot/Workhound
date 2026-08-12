from pathlib import Path
from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config.update(
        SECRET_KEY="workhound-v0.1.0-change-me",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + str(Path(app.instance_path) / "workhound.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=20 * 1024 * 1024,
    )
    db.init_app(app)
    from .routes import bp
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
    return app
