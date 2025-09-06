import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

from app import create_app

# The 'app' variable is what Gunicorn will look for
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))