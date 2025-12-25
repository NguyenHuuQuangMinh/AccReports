from functools import wraps
from flask import session, redirect, url_for, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        if session.get('role') != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function
