from app_factory import base_app
from Controllers.LadingPage.Link_controller import link_bp
from Controllers.LadingPage.auth_controller import auth_bp

app = base_app()

app.register_blueprint(link_bp)
app.register_blueprint(auth_bp)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8000, debug=True)