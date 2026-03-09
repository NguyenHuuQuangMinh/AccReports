from Controllers.MiSa.auth_controller import auth_bp
from Controllers.MiSa.Admin_controller import admin_bp
from Controllers.MiSa.user_controller import user_bp
from app_factory import base_app

app = base_app()

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8888, debug=True)
