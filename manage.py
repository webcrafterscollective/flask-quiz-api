import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use 0.0.0.0 to be accessible from outside the container in Docker
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
