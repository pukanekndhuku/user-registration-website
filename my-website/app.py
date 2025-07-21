# app.py
from flask import Flask, render_template, request
import gspread
import os
import json
from datetime import datetime

app = Flask(__name__)

# --- START: Google Sheets Connection ---
try:
    # Get the JSON credentials from the environment variable set in Vercel
    creds_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json_str:
        # This message will show in Vercel logs if the variable isn't set
        print("CRITICAL ERROR: GOOGLE_CREDENTIALS_JSON environment variable not set!")
        # In a real app, you might want to handle this more gracefully
        creds_dict = {}
    else:
        creds_dict = json.loads(creds_json_str)

    # Authenticate with gspread using the dictionary
    gc = gspread.service_account_from_dict(creds_dict)
    # --- IMPORTANT: Replace "Your Google Sheet Name" with the exact name of your sheet ---
    sh = gc.open("Your Google Sheet Name").sheet1
    print("Successfully connected to Google Sheets.")
    
except Exception as e:
    print(f"Error connecting to Google Sheets: {e}")
# --- END: Google Sheets Connection ---


@app.route('/')
def index():
    """Renders the main registration form page."""
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    """Handles the form submission and adds the data to the Google Sheet."""
    try:
        # Get data from the form submitted by the user
        mac = request.form['mac']
        api_key = request.form['apikey']
        end_date = request.form['enddate']
        
        # Prepare the new row with a "verified" status and timestamp
        status = "verified"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [mac, api_key, end_date, status, timestamp]

        # Add the new row to your Google Sheet
        sh.append_row(new_row)
        
        # Show a success message to the user
        return "<h1>Success!</h1><p>Your details have been registered.</p><a href='/'>Go Back</a>"

    except Exception as e:
        # Show an error message if anything goes wrong
        return f"<h1>Error</h1><p>Something went wrong: {e}</p><a href='/'>Try Again</a>"