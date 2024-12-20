# import eventlet
# eventlet.monkey_patch()

from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO,emit

from controller.auth.signup import signup_bp
from controller.auth.login import login_bp


app = Flask(__name__)

CORS(app, resources={r"/*": {
    "origins": "*",  # Change '*' to specific origins in production
    "allow_headers": ["Content-Type", "Authorization"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

# Initialize the Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20000 per day", "5000 per hour"]  # Adjust limits as needed
)

socketio = SocketIO(app, cors_allowed_origins="*")



@app.route("/", methods=['GET'])
def index():
    return jsonify({"message": "App access not allowed"})


#blueprint rest apis
app.register_blueprint(signup_bp)
app.register_blueprint(login_bp)

#websocket based routes

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Run the app with SocketIO support.