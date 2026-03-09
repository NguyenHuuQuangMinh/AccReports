from app2 import app
from waitress import serve

serve(app, host="0.0.0.0", port=8000)