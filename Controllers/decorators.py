from functools import wraps
from flask import session, redirect, url_for, abort, request, jsonify, g
from models.Misa.APIKey_model import APIKeyModel
from datetime import datetime

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_link(f):
    @wraps(f)
    def decorated_link_function(*args, **kwargs):
        if 'user_id_link' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_link_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        if session.get('role') != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return {"error": "API key required"}, 401

        models = APIKeyModel()
        row = models.check_API(api_key)

        if not row:
            return {"error": "Invalid API key or your User unavailable"}, 403

        if not row.Status:
            return {"error": "API key disabled"}, 403

        if datetime.now() > row.ExpiredAt:
            return {"error": "API key expired"}, 403

        g.api_user_id = row.UserId
        return f(*args, **kwargs)
    return wrapper

