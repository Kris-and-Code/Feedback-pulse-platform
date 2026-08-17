import os

from dotenv import load_dotenv
from flask import Flask

from app.legacy_routes import legacy_routes
from app.routes import api_routes

load_dotenv()


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="/frontend")
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", str(6 * 1024 * 1024)))
    app.config["JSON_SORT_KEYS"] = False

    app.register_blueprint(api_routes)
    app.register_blueprint(legacy_routes)

    @app.route("/ui")
    def ui():
        return app.send_static_file("index.html")

    @app.errorhandler(413)
    def request_too_large(_error):
        return {"error": "Uploaded file is too large"}, 413

    return app
