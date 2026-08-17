from app import create_app
import os

app = create_app()


def list_routes():
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule.rule}, Endpoint: {rule.endpoint}, Methods: {list(rule.methods)}")


if __name__ == "__main__":
    list_routes()
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host=os.getenv("FLASK_HOST", "127.0.0.1"), port=int(os.getenv("FLASK_PORT", "5000")))
