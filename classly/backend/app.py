"""
StudyHub Backend - Flask API Server
Aggregates coursework from Canvas, Gradescope, PrairieLearn, and Campuswire
"""

from routes.ai import ai_bp
from routes.auth import auth_bp
from routes.platforms import platforms_bp
from routes.schedule import schedule_bp
from routes.deadlines import deadlines_bp
from routes.calendar_oauth import calendar_oauth_bp
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import secrets

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Set secret key for sessions (required for OAuth flow)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)

# Import route blueprints
# CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)

# Import route blueprints
from routes.deadlines import deadlines_bp
from routes.schedule import schedule_bp
from routes.platforms import platforms_bp
from routes.auth import auth_bp
from routes.scrape import scrape_bp
from routes.rag import rag_bp
from routes.tasks import tasks_bp

# Register blueprints
app.register_blueprint(deadlines_bp, url_prefix='/api/deadlines')
app.register_blueprint(schedule_bp, url_prefix='/api/schedule')
app.register_blueprint(platforms_bp, url_prefix='/api/platforms')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(calendar_oauth_bp, url_prefix='/api/calendar')
app.register_blueprint(scrape_bp, url_prefix='/api/scrape')
app.register_blueprint(rag_bp, url_prefix='/api/rag')
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')


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
            "ai": "/api/ai",
            "calendar_oauth": "/api/calendar/oauth",
            "rag": "/api/rag",
            "tasks": "/api/tasks"
        }
    })


@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
