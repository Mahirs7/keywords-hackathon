"""
StudyHub Backend - Flask API Server
Aggregates coursework from Canvas, Gradescope, PrairieLearn, and Campuswire
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)

# Import route blueprints
from routes.deadlines import deadlines_bp
from routes.schedule import schedule_bp
from routes.platforms import platforms_bp
from routes.auth import auth_bp
from routes.scrape import scrape_bp
from routes.rag import rag_bp

# Register blueprints
app.register_blueprint(deadlines_bp, url_prefix='/api/deadlines')
app.register_blueprint(schedule_bp, url_prefix='/api/schedule')
app.register_blueprint(platforms_bp, url_prefix='/api/platforms')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(scrape_bp, url_prefix='/api/scrape')
app.register_blueprint(rag_bp, url_prefix='/api/rag')


@app.route('/')
def index():
    return jsonify({
        "name": "StudyHub API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "deadlines": "/api/deadlines",
            "schedule": "/api/schedule",
            "platforms": "/api/platforms",
            "auth": "/api/auth",
            "rag": "/api/rag"
        }
    })


@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
