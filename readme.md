Flask Quiz APIThis is the backend for the Quiz Application, built with Flask and using a blueprint architecture for scalability.SetupCreate a virtual environment:python -m venv .venv
source .venv/bin/activate
# On Windows: .venv\Scripts\activate
Install dependencies:pip install -r requirements.txt
Set up environment variables:Copy .env.example to .env and fill in the values.cp .env.example .env
Initialize and upgrade the database:flask db upgrade
Create the default admin user:flask create-admin
Running the Applicationflask run
The API will be available at http://localhost:5000.