from flask import Flask
from src.flask_app.routes import routes

# Initialize Flask app
app = Flask(__name__)

# Register Blueprint
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)