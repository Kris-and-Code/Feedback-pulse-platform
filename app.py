from app import create_app

# Initialize Flask app
app = create_app()

# List routes (debugging helper)
def list_routes():
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule.rule}, Endpoint: {rule.endpoint}, Methods: {list(rule.methods)}")

if __name__ == '__main__':
    list_routes()  # Print routes when the server starts
    app.run(debug=True)
