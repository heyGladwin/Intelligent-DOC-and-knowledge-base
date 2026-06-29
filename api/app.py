from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load .env before importing routes
load_dotenv()

from routes.chat_routes import chat_bp
from routes.document_routes import document_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Allows your Streamlit app to talk to this API

    # Register the different parts of our app
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(document_bp, url_prefix="/api/document")

    @app.route('/')
    def health_check():
        return jsonify({
            "status": "Backend is Online", 
            "version": "2026.1",
            "port": 5000
        })

    return app

if __name__ == "__main__":
    app = create_app()
    # Debug=True means it auto-restarts when you save changes
    app.run(debug=True, port=5000)