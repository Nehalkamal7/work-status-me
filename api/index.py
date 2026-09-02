import sys
import os

# Add backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir_option1 = os.path.join(current_dir, "..", "backend")
backend_dir_option2 = os.path.join(current_dir, "backend")
backend_dir_option3 = os.path.abspath("backend")

for b_dir in [backend_dir_option1, backend_dir_option2, backend_dir_option3]:
    if os.path.exists(b_dir) and b_dir not in sys.path:
        sys.path.insert(0, b_dir)

from app.main import app
from mangum import Mangum

handler = Mangum(app, api_gateway_base_path=None)
app = app
