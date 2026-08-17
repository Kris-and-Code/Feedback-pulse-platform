from flask import Flask

from app.legacy_routes import legacy_routes
from app.routes import api_routes


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="/frontend")

    app.register_blueprint(api_routes)
    app.register_blueprint(legacy_routes)

    @app.route("/ui")
    def ui():
        return app.send_static_file("index.html")

    return app
