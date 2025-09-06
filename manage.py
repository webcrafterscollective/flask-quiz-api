import os
from dotenv import load_dotenv

# Only load the .env file if the FLASK_CONFIG is not set to 'production'
if os.getenv('RAILWAY_ENVIRONMENT') != 'production':
    print("Not in Railway production, loading .env file for local development.")
    load_dotenv()

from app import create_app
from app.extensions import db
from app.models import User

# The 'app' variable is what Gunicorn will look for
app = create_app()

# --- Start of new code ---
# Register the custom CLI command
@app.cli.command("create-admin")
def create_admin():
    """Creates a default admin user from environment variables."""
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    password = os.environ.get('ADMIN_PASSWORD', 'adminpass')
    
    if User.query.filter_by(username=username).first():
        print("Admin user already exists.")
        return
        
    user = User(username=username, email=email, role='admin')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Admin user '{username}' created successfully.")
# --- End of new code ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))