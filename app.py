from flask import Flask
from Controllers.auth_controller import auth_bp
from Controllers.Admin_controller import admin_bp
from Controllers.user_controller import user_bp
from config.database import close_db
import os
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.teardown_appcontext(close_db)

if __name__ == '__main__':
    app.run(debug=True)
