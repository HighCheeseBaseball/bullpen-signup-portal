# Google Sheets Integration Setup Guide

This guide will help you set up Google Sheets integration for your Bullpen Signup Portal.

## Prerequisites

- A Google account
- Access to Google Cloud Console
- Your Google Sheet named "Bullpen Day Sheet"

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Enter project name: "Bullpen Signup Portal"
5. Click "Create"

### 2. Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API" and enable it
3. Search for "Google Drive API" and enable it

### 3. Create a Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Enter service account name: "bullpen-signup-service"
4. Enter description: "Service account for Bullpen Signup Portal"
5. Click "Create and Continue"
6. Skip the optional steps and click "Done"

### 4. Generate Credentials

1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create new key"
5. Select "JSON" format
6. Click "Create"
7. The JSON file will download automatically

### 5. Configure the Credentials File

1. Rename the downloaded JSON file to `google_credentials.json`
2. Move the file to your `Bullpen_Signup` folder
3. **Important**: Keep this file secure and never share it publicly

### 6. Share Your Google Sheet

1. Open your Google Sheet "Bullpen Day Sheet"
2. Click the "Share" button (top right)
3. Add the service account email (found in the JSON file under "client_email")
4. Give it "Editor" permissions
5. Click "Send"

### 7. Install Required Packages

Run this command in your terminal:

```bash
pip install gspread oauth2client
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Testing the Integration

1. Start your Streamlit app:
   ```bash
   python -m streamlit run app.py
   ```

2. Go to the Admin Dashboard
3. Enter the admin password: `admin123`
4. Click on the "Google Sheets" tab
5. Click "Test Google Sheets Connection"
6. If successful, you'll see a green checkmark

## How It Works

- **Automatic Sync**: Every new signup is automatically added to your Google Sheet
- **Real-time Updates**: Data appears in your sheet immediately after signup
- **Backup**: Your local CSV file is still maintained as a backup
- **Manual Sync**: You can manually sync all existing signups using the "Sync All Signups" button

## Troubleshooting

### Common Issues

1. **"Google credentials file not found"**
   - Make sure `google_credentials.json` is in the same folder as `app.py`
   - Check the file name is exactly `google_credentials.json`

2. **"Failed to connect to Google Sheets"**
   - Verify the service account email has access to your sheet
   - Check that the APIs are enabled in Google Cloud Console
   - Ensure the JSON file is valid

3. **"Sheet not found"**
   - Make sure your Google Sheet is named exactly "Bullpen Day Sheet"
   - Verify the service account has access to the sheet

### Getting Help

If you encounter issues:
1. Check the error messages in the Streamlit app
2. Verify all setup steps were completed correctly
3. Make sure your Google Sheet is shared with the service account

## Security Notes

- Never commit the `google_credentials.json` file to version control
- Keep your service account credentials secure
- Regularly rotate your service account keys if needed

## Sheet Structure

Your Google Sheet will automatically create a "Signups" worksheet with these columns:
- Athlete Name
- Email
- Phone
- Coach
- Signup Date
- Signup Time
- Preferred Date
- Preferred Time
- Status

The app will automatically format dates and times for easy reading.
