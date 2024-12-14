# Documentation
To run the project currently in flask phase you have to make the preperations accordingl:

# Update and upgrade system packages (optional but recommended)
sudo apt update && sudo apt upgrade -y

# Install Python 3, pip, and venv if not already installed
sudo apt install python3 python3-pip python3-venv -y

# Navigate to the project directory (replace /path/to/antiradicalshield with your actual path)
cd /path/to/antiradicalshield

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python3 setup_db.py

# Run the Flask app
python3 app.py
