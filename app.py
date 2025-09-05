import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import os
import csv
from typing import List, Dict, Optional
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set page config
st.set_page_config(
    page_title="Bullpen Sign-up Portal",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force dark mode
st.markdown("""
<style>
    .stApp {
        color: white;
        background-color: #0e1117;
    }
    .stApp > header {
        background-color: transparent;
    }
    .stApp > div > div > div > div {
        background-color: #0e1117;
    }
    .stSidebar {
        background-color: #262730;
    }
    .stSidebar > div > div > div > div {
        background-color: #262730;
    }
    .stSelectbox > div > div {
        background-color: #262730;
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
    }
    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: white;
    }
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
    }
    .stButton > button:hover {
        background-color: #ff6b6b;
    }
    .stForm {
        background-color: #262730;
    }
    .stInfo {
        background-color: #1f2937;
        border: 1px solid #374151;
    }
    .stSuccess {
        background-color: #064e3b;
        border: 1px solid #065f46;
    }
    .stError {
        background-color: #7f1d1d;
        border: 1px solid #991b1b;
    }
    .stWarning {
        background-color: #78350f;
        border: 1px solid #92400e;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .time-slot {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .time-slot:hover {
        background-color: #e9ecef;
    }
    .time-slot.available {
        border-color: #28a745;
        background-color: #d4edda;
    }
    .time-slot.full {
        border-color: #dc3545;
        background-color: #f8d7da;
    }
    .time-slot.past {
        border-color: #6c757d;
        background-color: #e9ecef;
        opacity: 0.6;
    }
    .athlete-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Data file paths
SIGNUPS_FILE = "signups.csv"
SETTINGS_FILE = "settings.json"

# Google Sheets configuration
GOOGLE_SHEETS_CONFIG = {
    "sheet_name": "Day Sheet '25",  # Change this to your actual sheet name
    "worksheet_name": "Online Bullpen Sign-Ups",
    "credentials_file": "google_credentials.json"  # Replace with your new credentials file
}

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "cspbullpen@gmail.com",  # Your Gmail address
    "recipient_email": "cspflorida@gmail.com",  # Where to send notifications
    "app_password": "epfm jgxz oznu anwf"  # Gmail App Password (you'll need to set this up)
}

# Default settings
DEFAULT_SETTINGS = {
    "max_athletes_per_slot": 4,
    "cutoff_hours": 16,
    "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    "time_slots": [
        "9:00 AM", "9:15 AM", "9:30 AM", "9:45 AM",
        "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM",
        "11:00 AM", "11:15 AM", "11:30 AM", "11:45 AM",
        "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM",
        "1:00 PM", "1:15 PM", "1:30 PM", "1:45 PM",
        "2:00 PM", "2:15 PM", "2:30 PM", "2:45 PM",
        "3:00 PM", "3:15 PM", "3:30 PM", "3:45 PM",
        "4:00 PM", "4:15 PM", "4:30 PM", "4:45 PM",
        "5:00 PM", "5:15 PM", "5:30 PM", "5:45 PM",
        "6:00 PM"
    ],
    "facility_name": "Bullpen Training Facility"
}

def load_settings() -> Dict:
    """Load settings from JSON file or create default"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings: Dict):
    """Save settings to JSON file"""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def load_sign_ups() -> pd.DataFrame:
    """Load sign-ups from CSV file or create empty DataFrame"""
    if os.path.exists(SIGNUPS_FILE):
        try:
            df = pd.read_csv(SIGNUPS_FILE)
            if not df.empty:
                df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
                df['preferred_date'] = pd.to_datetime(df['preferred_date'], errors='coerce')
                
                # Drop rows with invalid dates
                df = df.dropna(subset=['signup_date', 'preferred_date'])
                
                # Ensure all required columns exist
                required_columns = ['athlete_name', 'email', 'phone', 'coach', 'signup_date', 'preferred_date', 'preferred_time', 'notes', 'status']
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = ''
            else:
                # Create empty DataFrame with proper datetime columns
                df = pd.DataFrame(columns=[
                    'athlete_name', 'email', 'phone', 'coach', 'signup_date',
                    'preferred_date', 'preferred_time', 'notes', 'status'
                ])
                df['signup_date'] = pd.to_datetime([])
                df['preferred_date'] = pd.to_datetime([])
            return df
        except Exception as e:
            print(f"Error loading sign-ups: {e}")
            # Create empty DataFrame with proper datetime columns
            df = pd.DataFrame(columns=[
                'athlete_name', 'email', 'phone', 'coach', 'signup_date',
                'preferred_date', 'preferred_time', 'notes', 'status'
            ])
            df['signup_date'] = pd.to_datetime([])
            df['preferred_date'] = pd.to_datetime([])
            return df
    
    # Create empty DataFrame with proper datetime columns
    df = pd.DataFrame(columns=[
        'athlete_name', 'email', 'phone', 'coach', 'signup_date',
        'preferred_date', 'preferred_time', 'notes', 'status'
    ])
    df['signup_date'] = pd.to_datetime([])
    df['preferred_date'] = pd.to_datetime([])
    return df

def save_sign_ups(df: pd.DataFrame):
    """Save sign-ups to CSV file"""
    df.to_csv(SIGNUPS_FILE, index=False)

def is_within_cutoff(preferred_date: datetime.date, cutoff_hours: int) -> bool:
    """Check if the preferred date is within the cutoff period"""
    now = datetime.datetime.now()
    cutoff_time = now + timedelta(hours=cutoff_hours)
    
    # Allow all dates from tomorrow onwards
    if preferred_date > now.date():
        return True
    
    # For same day, check if it's within cutoff
    preferred_datetime = datetime.datetime.combine(preferred_date, datetime.time.min)
    return preferred_datetime >= cutoff_time

def is_time_slot_within_cutoff(preferred_date: datetime.date, preferred_time: str, cutoff_hours: int) -> bool:
    """Check if the specific date and time combination is within the cutoff period"""
    now = datetime.datetime.now()
    cutoff_time = now + timedelta(hours=cutoff_hours)
    
    # Parse the preferred time
    try:
        # Handle various time formats (e.g., "9:30AM", "9:30 AM", "09:30 AM")
        time_str = preferred_time.strip().upper()
        
        # Remove AM/PM and extract time
        if 'AM' in time_str:
            time_part = time_str.replace('AM', '').strip()
            is_pm = False
        elif 'PM' in time_str:
            time_part = time_str.replace('PM', '').strip()
            is_pm = True
        else:
            # Assume AM if no AM/PM specified
            time_part = time_str
            is_pm = False
        
        # Parse hour and minute
        if ':' in time_part:
            hour, minute = time_part.split(':')
            hour = int(hour.strip())
            minute = int(minute.strip())
        else:
            hour = int(time_part.strip())
            minute = 0
        
        # Convert to 24-hour format
        if is_pm and hour != 12:
            hour += 12
        elif not is_pm and hour == 12:
            hour = 0
        
        # Create datetime object
        preferred_datetime = datetime.datetime.combine(preferred_date, datetime.time(hour, minute))
        
        # Check if it's within cutoff
        return preferred_datetime >= cutoff_time
        
    except (ValueError, IndexError):
        # If time parsing fails, return False (invalid time format)
        return False

def get_available_slots(preferred_date: datetime.date, time_slots: List[str], 
                       sign_ups_df: pd.DataFrame, max_per_slot: int) -> Dict[str, int]:
    """Get available slots for a given date"""
    available = {}
    
    for time_slot in time_slots:
        # Count current signups for this date and time
        current_signups = len(sign_ups_df[
            (sign_ups_df['preferred_date'].dt.date == preferred_date) & 
            (sign_ups_df['preferred_time'] == time_slot) &
            (sign_ups_df['status'] == 'confirmed')
        ])
        
        available[time_slot] = max(0, max_per_slot - current_signups)
    
    return available

def is_past_slot(preferred_date: datetime.date, time_slot: str) -> bool:
    """Check if a time slot is in the past"""
    slot_time = datetime.datetime.strptime(time_slot, "%I:%M %p").time()
    slot_datetime = datetime.datetime.combine(preferred_date, slot_time)
    return slot_datetime < datetime.datetime.now()

def get_google_sheets_client():
    """Initialize and return Google Sheets client"""
    try:
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Try to get credentials from Streamlit secrets first, then fallback to file
        try:
            # Get credentials from Streamlit secrets
            credentials_data = st.secrets["GOOGLE_CREDENTIALS"]
            
            # Handle both string and dict formats
            if isinstance(credentials_data, str):
                import json
                credentials_json = json.loads(credentials_data)
            else:
                credentials_json = credentials_data
            
            # Fix private key formatting if it's a string
            if 'private_key' in credentials_json and isinstance(credentials_json['private_key'], str):
                # Replace \\n with actual newlines
                credentials_json['private_key'] = credentials_json['private_key'].replace('\\n', '\n')
                
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                credentials_json, scope
            )
        except Exception as e:
            st.error(f"Error loading credentials from secrets: {str(e)}")
            # Fallback to file-based credentials
            if not os.path.exists(GOOGLE_SHEETS_CONFIG["credentials_file"]):
                return None
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_SHEETS_CONFIG["credentials_file"], scope
            )
        
        # Authorize and create client
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return None

def get_google_sheet():
    """Get the Google Sheet and worksheet"""
    try:
        client = get_google_sheets_client()
        if not client:
            return None, None
        
        # Open the spreadsheet
        sheet = client.open(GOOGLE_SHEETS_CONFIG["sheet_name"])
        
        # Get or create the worksheet
        try:
            worksheet = sheet.worksheet(GOOGLE_SHEETS_CONFIG["worksheet_name"])
        except gspread.WorksheetNotFound:
            # Create worksheet if it doesn't exist
            worksheet = sheet.add_worksheet(
                title=GOOGLE_SHEETS_CONFIG["worksheet_name"], 
                rows=1000, 
                cols=10
            )
            # Add headers
            headers = ['Athlete Name', 'Email', 'Phone', 'Coach', 'Sign-up Date', 'Sign-up Time', 'Preferred Date', 'Preferred Time', 'Notes']
            worksheet.append_row(headers)
        
        return sheet, worksheet
    except gspread.SpreadsheetNotFound:
        st.error(f"Google Sheet '{GOOGLE_SHEETS_CONFIG['sheet_name']}' not found. Please check the sheet name and sharing permissions.")
        return None, None
    except gspread.WorksheetNotFound:
        st.error(f"Worksheet '{GOOGLE_SHEETS_CONFIG['worksheet_name']}' not found in the sheet.")
        return None, None
    except Exception as e:
        st.error(f"Error accessing Google Sheet: {str(e)}")
        return None, None

def add_sign_up_to_google_sheets(sign_up_data: Dict):
    """Add a new sign-up to Google Sheets"""
    try:
        sheet, worksheet = get_google_sheet()
        if not worksheet:
            return False
        
        # Convert UTC time to Eastern Time for display
        import pytz
        utc_time = sign_up_data['signup_date']
        eastern = pytz.timezone('US/Eastern')
        local_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(eastern)
        
        # Format the data for Google Sheets
        row_data = [
            sign_up_data['athlete_name'],
            sign_up_data['email'],
            sign_up_data['phone'],
            sign_up_data['coach'],
            local_time.strftime('%m/%d/%Y'),
            local_time.strftime('%I:%M %p'),
            sign_up_data['preferred_date'].strftime('%m/%d/%Y'),
            sign_up_data['preferred_time'],
            sign_up_data['notes']
        ]
        
        # Add the row
        worksheet.append_row(row_data)
        return True
    except gspread.exceptions.APIError as e:
        st.error(f"Google Sheets API Error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Error adding sign-up to Google Sheets: {str(e)}")
        return False

def sync_all_sign_ups_to_google_sheets():
    """Sync all existing sign-ups to Google Sheets"""
    try:
        sign_ups_df = load_sign_ups()
        if sign_ups_df.empty:
            return True
        
        sheet, worksheet = get_google_sheet()
        if not worksheet:
            return False
        
        # Clear existing data (except headers)
        worksheet.clear()
        
        # Add headers
        headers = ['Athlete Name', 'Email', 'Phone', 'Coach', 'Sign-up Date', 'Sign-up Time', 'Preferred Date', 'Preferred Time', 'Notes']
        worksheet.append_row(headers)
        
        # Add all sign-ups
        for _, row in sign_ups_df.iterrows():
            # Convert UTC time to Eastern Time for display
            import pytz
            utc_time = row['signup_date']
            eastern = pytz.timezone('US/Eastern')
            local_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(eastern)
            
            row_data = [
                row['athlete_name'],
                row['email'],
                row['phone'],
                row['coach'],
                local_time.strftime('%m/%d/%Y'),
                local_time.strftime('%I:%M %p'),
                row['preferred_date'].strftime('%m/%d/%Y'),
                row['preferred_time'],
                row.get('notes', '')  # Use get() to handle existing data without notes
            ]
            worksheet.append_row(row_data)
        
        return True
    except Exception as e:
        st.error(f"Error syncing to Google Sheets: {str(e)}")
        return False

def send_sign_up_notification(sign_up_data: Dict):
    """Send email notification for new sign-up"""
    try:
        # Get app password from Streamlit secrets or config
        app_password = st.secrets.get("GMAIL_APP_PASSWORD", EMAIL_CONFIG["app_password"])
        
        # Check if email is configured
        if not app_password:
            st.warning("Email notifications not configured. Please set up Gmail App Password in Streamlit secrets.")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender_email"]
        msg['To'] = EMAIL_CONFIG["recipient_email"]
        msg['Subject'] = f"New Bullpen Sign-up - {sign_up_data['athlete_name']}"
        
        # Convert UTC time to Eastern Time for display
        import pytz
        utc_time = sign_up_data['signup_date']
        eastern = pytz.timezone('US/Eastern')
        local_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(eastern)
        
        # Create email body
        body = f"""
New Bullpen Sign-up Received!

Athlete Details:
- Name: {sign_up_data['athlete_name']}
- Phone: {sign_up_data['phone']}
- Email: {sign_up_data['email'] if sign_up_data['email'] else 'Not provided'}
- Coach: {sign_up_data['coach']}
- Date: {sign_up_data['preferred_date'].strftime('%A, %B %d, %Y')}
- Time: {sign_up_data['preferred_time']}
- Notes: {sign_up_data['notes'] if sign_up_data['notes'] else 'None'}

Sign-up Time: {local_time.strftime('%A, %B %d, %Y at %I:%M %p')} (Eastern Time)

---
This is an automated notification from the Bullpen Sign-up Portal.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["sender_email"], app_password)
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["recipient_email"], text)
        server.quit()
        
        return True
        
    except Exception as e:
        st.error(f"Error sending email notification: {str(e)}")
        return False

def athlete_sign_up_page():
    """Main athlete sign-up page"""
    # Logo at the top
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.image("cressey_logo.png", width=400)
    
    
    # Load settings and sign-ups
    settings = load_settings()
    sign_ups_df = load_sign_ups()
    
    # Athlete information form
    st.markdown("### Athlete Information")
    
    with st.form("athlete_signup_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            athlete_name = st.text_input("Full Name *", placeholder="Enter your full name")
            email = st.text_input("Email Address (optional)", placeholder="your.email@example.com")
        
        with col2:
            phone = st.text_input("Phone Number *", placeholder="(555) 123-4567")
            coach = st.selectbox("Bullpen Coach *", ["Austin Henrich", "Matt Minnick", "Nicho Fernandez", "Spencer Stockton"], placeholder="Select your coach")
        
        # Date selection
        st.markdown("### Select Date")
        
        # Get available dates (next 30 days, excluding past dates and respecting cutoff)
        today = datetime.date.today()
        available_dates = []
        
        for i in range(1, 31):  # Start from 1 to ensure tomorrow is included
            check_date = today + timedelta(days=i)
            # Check if date is within cutoff and is an available day
            if (is_within_cutoff(check_date, settings['cutoff_hours']) and 
                check_date.strftime('%A') in settings['available_days']):
                available_dates.append(check_date)
        
        if not available_dates:
            st.error("No available dates within the cutoff period. Please try again later.")
            return
        
        selected_date = st.selectbox(
            "Choose your date:",
            available_dates,
            format_func=lambda x: x.strftime("%A, %B %d, %Y")
        )
        
        # Time input
        st.markdown("### Select Time")
        st.info("Must sign-up 16 hours in advance")
        selected_time = st.text_input("Choose Preferred Time (9:00 AM - 6:00 PM):", placeholder="10:15AM")
        
        # Notes section
        st.markdown("### Additional Notes (Optional)")
        notes = st.text_area("Notes for your bullpen session:", placeholder="Any specific areas you want to work on, equipment needed, etc.", height=100)
        
        # Submit button
        submitted = st.form_submit_button("Submit Sign-up", type="primary")
        
        if submitted:
            # Validation
            if not all([athlete_name, phone, coach, selected_time]):
                st.error("Please fill in all required fields (Name, Phone, Coach, and Time).")
                return
            
            # Check if the selected time slot is within the cutoff period
            if not is_time_slot_within_cutoff(selected_date, selected_time, settings['cutoff_hours']):
                st.error(f"❌ Cannot sign up for {selected_time} on {selected_date.strftime('%A, %B %d, %Y')}. You must sign up at least {settings['cutoff_hours']} hours in advance.")
                return
            
            # Add new sign-up
            new_signup = pd.DataFrame([{
                'athlete_name': athlete_name,
                'email': email,
                'phone': phone,
                'coach': coach,
                'signup_date': datetime.datetime.now(),
                'preferred_date': pd.to_datetime(selected_date),
                'preferred_time': selected_time,
                'notes': notes if notes else '',
                'status': 'confirmed'
            }])
            
            # Save sign-up
            updated_df = pd.concat([sign_ups_df, new_signup], ignore_index=True)
            save_sign_ups(updated_df)
            
            # Add to Google Sheets
            sign_up_data = {
                'athlete_name': athlete_name,
                'email': email,
                'phone': phone,
                'coach': coach,
                'signup_date': datetime.datetime.now(),
                'preferred_date': selected_date,
                'preferred_time': selected_time,
                'notes': notes if notes else ''
            }
            
            google_sheets_success = add_sign_up_to_google_sheets(sign_up_data)
            
            # Send email notification
            email_success = send_sign_up_notification(sign_up_data)
            
            # Success message
            email_display = f'<p style="color: black;"><strong>Email:</strong> {email}</p>' if email else ''
            
            st.markdown(f"""
            <div class="success-box">
                <h3 style="color: black;">Sign-up Successful!</h3>
                <p style="color: black;"><strong>Name:</strong> {athlete_name}</p>
                <p style="color: black;"><strong>Date:</strong> {selected_date.strftime('%A, %B %d, %Y')}</p>
                <p style="color: black;"><strong>Time:</strong> {selected_time}</p>
                <p style="color: black;"><strong>Phone:</strong> {phone}</p>
                <p style="color: black;"><strong>Coach:</strong> {coach}</p>
                {email_display}
            </div>
            """, unsafe_allow_html=True)

def admin_page():
    """Administrative page for managing signups and settings"""
    # Logo at the top
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.image("cressey_logo.png", width=400)
    
    st.markdown('<h1 class="main-header">🔧 Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    settings = load_settings()
    sign_ups_df = load_sign_ups()
    
    # Admin tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["View Signups", "Schedule Export", "Settings", "Google Sheets", "Email Settings"])
    
    with tab1:
        st.markdown("### Current Signups")
        
        if sign_ups_df.empty:
            st.info("No signups yet.")
        else:
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_filter = st.date_input("Filter by date", value=None)
            
            with col2:
                status_filter = st.selectbox("Filter by status", ["All", "confirmed", "cancelled"])
            
            with col3:
                if st.button("Clear Filters"):
                    date_filter = None
                    status_filter = "All"
            
            # Apply filters
            filtered_df = sign_ups_df.copy()
            
            if date_filter:
                filtered_df = filtered_df[filtered_df['preferred_date'].dt.date == date_filter]
            
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            # Display filtered results
            if not filtered_df.empty:
                display_df = filtered_df[['athlete_name', 'email', 'phone', 'coach', 'signup_date', 'preferred_date', 'preferred_time', 'notes', 'status']].copy()
                
                # Map coach names to initials
                coach_initials = {
                    'Austin Henrich': 'AH',
                    'Spencer Stockton': 'SS',
                    'Nicho Fernandez': 'NF',
                    'Matt Minnick': 'MM'
                }
                display_df['coach'] = display_df['coach'].map(coach_initials).fillna(display_df['coach'])
                
                # Format date and time columns
                display_df['Sign-up Date'] = display_df['signup_date'].dt.strftime('%m/%d/%Y')
                display_df['Sign-up Time'] = display_df['signup_date'].dt.strftime('%I:%M %p')
                
                # Reorder columns
                display_df = display_df[['athlete_name', 'email', 'phone', 'coach', 'Sign-up Date', 'Sign-up Time', 'preferred_date', 'preferred_time', 'notes', 'status']]
                display_df.columns = ['Name', 'Email', 'Phone', 'Coach', 'Sign-up Date', 'Sign-up Time', 'Preferred Date', 'Preferred Time', 'Notes', 'Status']
                
                # Format preferred date
                display_df['Preferred Date'] = display_df['Preferred Date'].dt.strftime('%m/%d/%Y')
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Sign-ups", len(filtered_df))
                with col2:
                    confirmed_count = len(filtered_df[filtered_df['status'] == 'confirmed'])
                    st.metric("Confirmed", confirmed_count)
                with col3:
                    cancelled_count = len(filtered_df[filtered_df['status'] == 'cancelled'])
                    st.metric("Cancelled", cancelled_count)
            else:
                st.info("No sign-ups match the selected filters.")
    
    with tab2:
        st.markdown("### Export Schedule")
        
        # Date range selection
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start Date", value=datetime.date.today())
        
        with col2:
            end_date = st.date_input("End Date", value=datetime.date.today() + timedelta(days=7))
        
        if st.button("Generate Schedule"):
            # Filter signups by date range
            schedule_df = sign_ups_df[
                (sign_ups_df['preferred_date'].dt.date >= start_date) &
                (sign_ups_df['preferred_date'].dt.date <= end_date) &
                (sign_ups_df['status'] == 'confirmed')
            ].copy()
            
            if schedule_df.empty:
                st.warning("No confirmed signups in the selected date range.")
            else:
                # Sort by date and time
                schedule_df = schedule_df.sort_values(['preferred_date', 'preferred_time'])
                
                st.markdown("### Schedule Preview")
                
                display_df = schedule_df[['athlete_name', 'email', 'phone', 'coach', 'signup_date', 'preferred_date', 'preferred_time', 'notes', 'status']].copy()
                
                # Map coach names to initials
                coach_initials = {
                    'Austin Henrich': 'AH',
                    'Spencer Stockton': 'SS',
                    'Nicho Fernandez': 'NF',
                    'Matt Minnick': 'MM'
                }
                display_df['coach'] = display_df['coach'].map(coach_initials).fillna(display_df['coach'])
                
                # Format date and time columns
                display_df['Sign-up Date'] = display_df['signup_date'].dt.strftime('%m/%d/%Y')
                display_df['Sign-up Time'] = display_df['signup_date'].dt.strftime('%I:%M %p')
                
                # Reorder columns
                display_df = display_df[['athlete_name', 'email', 'phone', 'coach', 'Sign-up Date', 'Sign-up Time', 'preferred_date', 'preferred_time', 'notes', 'status']]
                display_df.columns = ['Name', 'Email', 'Phone', 'Coach', 'Sign-up Date', 'Sign-up Time', 'Preferred Date', 'Preferred Time', 'Notes', 'Status']
                
                # Format preferred date
                display_df['Preferred Date'] = display_df['Preferred Date'].dt.strftime('%m/%d/%Y')
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Export options
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV download
                    csv_data = schedule_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"bullpen_schedule_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Excel download (if openpyxl is available)
                    try:
                        import openpyxl
                        from io import BytesIO
                        
                        excel_buffer = BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            schedule_df.to_excel(writer, sheet_name='Schedule', index=False)
                        
                        st.download_button(
                            label="Download Excel",
                            data=excel_buffer.getvalue(),
                            file_name=f"bullpen_schedule_{start_date}_{end_date}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except ImportError:
                        st.info("Excel export requires openpyxl package")
    
    with tab3:
        st.markdown("### System Settings")
        
        with st.form("settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                facility_name = st.text_input("Facility Name", value=settings['facility_name'])
                cutoff_hours = st.number_input("Cutoff Hours", 
                                             min_value=1, max_value=168, 
                                             value=settings['cutoff_hours'])
            
            with col2:
                available_days = st.multiselect("Available Days", 
                                              ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                              default=settings['available_days'])
                
                # Time slots
                st.markdown("**Time Slots:**")
                time_slots_text = st.text_area("Enter time slots (one per line)", 
                                             value="\n".join(settings['time_slots']))
            
            if st.form_submit_button("Save Settings"):
                # Parse time slots
                time_slots = [slot.strip() for slot in time_slots_text.split('\n') if slot.strip()]
                
                # Update settings
                new_settings = {
                    "facility_name": facility_name,
                    "max_athletes_per_slot": settings['max_athletes_per_slot'],  # Keep existing value
                    "cutoff_hours": cutoff_hours,
                    "available_days": available_days,
                    "time_slots": time_slots
                }
                
                save_settings(new_settings)
                st.success("Settings saved successfully!")
                st.rerun()
    
    with tab4:
        st.markdown("### Google Sheets Integration")
        
        # Check if credentials are available (secrets or file)
        credentials_available = False
        try:
            # Check if credentials are in Streamlit secrets
            if "GOOGLE_CREDENTIALS" in st.secrets:
                st.success("✅ Google credentials found in Streamlit secrets")
                credentials_available = True
        except:
            pass
        
        if not credentials_available and os.path.exists(GOOGLE_SHEETS_CONFIG["credentials_file"]):
            st.success("✅ Google credentials file found")
            credentials_available = True
        
        if credentials_available:
            
            # Test connection
            if st.button("Test Google Sheets Connection"):
                # First test: Check if credentials are valid JSON
                try:
                    import json
                    credentials_json = st.secrets["GOOGLE_CREDENTIALS"]
                    json.loads(credentials_json)  # Test if it's valid JSON
                    st.info("✅ Credentials are valid JSON format")
                except Exception as e:
                    st.error(f"❌ Credentials are not valid JSON: {str(e)}")
                    return
                
                # Second test: Try to create client
                client = get_google_sheets_client()
                if client:
                    # Test actual sheet access
                    try:
                        sheet, worksheet = get_google_sheet()
                        if sheet and worksheet:
                            st.success("✅ Successfully connected to Google Sheets!")
                            st.info(f"Connected to sheet: '{sheet.title}' with worksheet: '{worksheet.title}'")
                        else:
                            st.error("❌ Connected to Google Sheets but couldn't access the specific sheet/worksheet")
                    except Exception as e:
                        st.error(f"❌ Connected to Google Sheets but error accessing sheet: {str(e)}")
                else:
                    st.error("❌ Failed to connect to Google Sheets - check credentials")
            
            # Sync all sign-ups
            if st.button("Sync All Sign-ups to Google Sheets"):
                with st.spinner("Syncing sign-ups..."):
                    success = sync_all_sign_ups_to_google_sheets()
                    if success:
                        st.success("✅ All sign-ups synced to Google Sheets!")
                    else:
                        st.error("❌ Failed to sync sign-ups")
            
            # Show current sheet info
            st.markdown("**Current Configuration:**")
            st.info(f"""
            - **Sheet Name:** {GOOGLE_SHEETS_CONFIG['sheet_name']}
            - **Worksheet:** {GOOGLE_SHEETS_CONFIG['worksheet_name']}
            - **Credentials File:** {GOOGLE_SHEETS_CONFIG['credentials_file']}
            """)
        
        else:
            st.error("❌ Google credentials not found")
            st.info("Please add GOOGLE_CREDENTIALS to Streamlit secrets or create the credentials file.")
            st.markdown("""
            **Setup Instructions:**
            
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select existing one
            3. Enable Google Sheets API and Google Drive API
            4. Create a Service Account
            5. Download the JSON credentials file
            6. Add the credentials to Streamlit secrets as GOOGLE_CREDENTIALS
            7. Share your Google Sheet with the service account email
            """)
    
    with tab5:
        st.markdown("### Email Notification Settings")
        
        st.markdown("**Current Configuration:**")
        st.info(f"""
        - **Sender Email:** {EMAIL_CONFIG['sender_email']}
        - **Recipient Email:** {EMAIL_CONFIG['recipient_email']}
        - **Status:** {'✅ Configured' if EMAIL_CONFIG['app_password'] else '❌ Not configured'}
        """)
        
        
        if st.button("Test Email Configuration"):
            test_data = {
                'athlete_name': 'Test User',
                'email': 'test@example.com',
                'phone': '(555) 123-4567',
                'coach': 'Austin Henrich',
                'signup_date': datetime.datetime.now(),
                'preferred_date': datetime.date.today() + timedelta(days=1),
                'preferred_time': '10:00 AM',
                'notes': 'This is a test sign-up'
            }
            
            with st.spinner("Sending test email..."):
                success = send_sign_up_notification(test_data)
                if success:
                    st.success("✅ Test email sent successfully!")
                else:
                    st.error("❌ Failed to send test email. Check your app password configuration.")

def main():
    """Main application"""
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page:", ["Athlete Sign-up", "Admin Dashboard"])
    
    if page == "Athlete Sign-up":
        athlete_sign_up_page()
    else:
        # Simple password protection for admin
        admin_password = st.sidebar.text_input("Admin Password", type="password")
        if admin_password == "admin123":  # Change this to a more secure password
            admin_page()
        elif admin_password:
            st.error("Incorrect password")
        else:
            st.info("Enter admin password to access dashboard")

if __name__ == "__main__":
    main()