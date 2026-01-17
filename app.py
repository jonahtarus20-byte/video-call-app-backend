from flask import Flask, redirect, jsonify
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from config import Config
from models import db, bcrypt
from errors import APIError
from jwt.exceptions import DecodeError, InvalidTokenError

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Initialize SocketIO with CORS

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Invalid token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Missing authorization token"}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return jsonify({"message": "Token has expired"}), 401

api = Api(
    app,
    title="Video Call API",
    version="1.0",
    description="Backend API for Video Call App",
    doc="/docs",
    prefix="/api"
)

from resources.auth import api as auth_ns
from resources.rooms import api as rooms_ns
import signaling  # Import signaling to register SocketIO events

api.add_namespace(auth_ns, path="/auth")
api.add_namespace(rooms_ns, path="/rooms")

@api.errorhandler(APIError)
def handle_api_error(error):
    return {"message": error.message}, error.status_code

@api.errorhandler(Exception)
def handle_exception(error):
    import traceback
    traceback.print_exc()
    return {"message": str(error)}, 500

@app.route("/")
def index():
    return redirect("/docs")

@app.route("/home")
def home():
    return {
        "message": "Video Call API",
        "version": "1.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "auth": "/api/auth",
            "rooms": "/api/rooms"
        }
    }, 200

@app.route("/api/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
