from flask import Flask
from config.database import close_db
from Controllers.extensions import limiter
from datetime import timedelta
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
import os
csrf = CSRFProtect()
def base_app():
    app = Flask(__name__)
    csrf.init_app(app)

    @app.context_processor
    def inject_csrf():
        return dict(csrf_token=generate_csrf)

    limiter.init_app(app)
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
    app.teardown_appcontext(close_db)

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3650)
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_SAMESITE='Lax'
    )

    return app