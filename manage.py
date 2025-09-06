import os
from dotenv import load_dotenv

# --- Start of fix ---
# Only load the .env file if the FLASK_CONFIG is not set to 'production'
if os.getenv('FLASK_CONFIG') != 'production':
    print("Running in development mode, loading .env file.")
    load_dotenv()
# --- End of fix ---

from app import create_app

# The 'app' variable is what Gunicorn will look for
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))