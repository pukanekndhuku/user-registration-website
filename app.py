# app.py - Updated and More Robust Version
from flask import Flask, render_template, request
import gspread
import os
import json
from datetime import datetime

app = Flask(__name__)

# --- Global variable for the sheet connection ---
sh = None
connection_error = None

# --- Function to connect to Google Sheets ---
def connect_to_sheet():
    global sh, connection_error
    try:
        # Get the JSON credentials from the environment variable set in Vercel
        creds_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not creds_json_str:
            connection_error = "CRITICAL ERROR: GOOGLE_CREDENTIALS_JSON environment variable not set in Vercel!"
            print(connection_error)
            return

        creds_dict = json.loads(creds_json_str)

        # Authenticate with gspread
        gc = gspread.service_account_from_dict(creds_dict)
        
        # --- IMPORTANT: Replace "Your Google Sheet Name" with the exact name of your sheet ---
        sheet_name = "My Users" # <--- MAKE SURE THIS NAME IS EXACTLY CORRECT
        sh = gc.open(sheet_name).sheet1
        
        print(f"Successfully connected to Google Sheet: '{sheet_name}'")
        
    except gspread.exceptions.SpreadsheetNotFound:
        connection_error = f"ERROR: The Google Sheet named '{sheet_name}' was not found. Check for typos or if the sheet exists."
        print(connection_error)
    except Exception as e:
        connection_error = f"An unexpected error occurred during Google Sheet connection: {e}"
        print(connection_error)

# --- Connect to the sheet when the application starts ---
connect_to_sheet()

@app.route('/')
def index():
    """Renders the main registration form page."""
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    """Handles the form submission and adds the data to the Google Sheet."""
    
    # First, check if the sheet connection was successful
    if sh is None:
        # If 'sh' was never assigned, it means the connection failed on startup.
        # Show a user-friendly error and log the detailed error.
        return f"<h1>Server Configuration Error</h1><p>The server could not connect to the database. Please contact the administrator.</p><p><i>Detail: {connection_error}</i></p>"

    try:
        # Get data from the form submitted by the user
        mac = request.form['mac']
        api_key = request.form['apikey']
        end_date = request.form['enddate']
        
        # Prepare the new row
        status = "verified"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [mac, api_key, end_date, status, timestamp]

        # Add the new row to your Google Sheet
        sh.append_row(new_row)
        
        # Show a success message
        return "<h1>Success!</h1><p>Your details have been registered.</p><a href='/'>Go Back</a>"

    except Exception as e:
        # Handle other potential errors during submission
        return f"<h1>Error During Submission</h1><p>An error occurred: {e}</p><a href='/'>Try Again</a>"
