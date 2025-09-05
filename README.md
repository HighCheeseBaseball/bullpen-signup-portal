# Bullpen Signup Portal

A web-based signup portal for athletes to reserve bullpen training sessions with automatic scheduling and administrative management.

## Features

### For Athletes
- **Easy Signup**: Simple form to register for bullpen sessions
- **Real-time Availability**: See available time slots and capacity
- **16-Hour Cutoff**: Automatic validation prevents last-minute signups
- **Confirmation**: Instant confirmation with session details

### For Administrators
- **Dashboard**: View all signups and manage the system
- **Schedule Export**: Export schedules to CSV or Excel format
- **Analytics**: Track usage patterns and popular time slots
- **Settings Management**: Configure facility settings, time slots, and capacity

## Quick Start

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the application**:
   ```bash
   python -m streamlit run app.py
   ```
   
   **Or on Windows**: Double-click `run_app.bat` or `run_app_advanced.bat`

2. **Open your browser** to the URL shown in the terminal (usually `http://localhost:8501`)

3. **Access the portal**:
   - **Athletes**: Use the "Athlete Signup" page to register for sessions
   - **Admins**: Use the "Admin Dashboard" page (password: `admin123`)

## Configuration

### Default Settings
- **Cutoff hours**: 16 hours advance notice required
- **Available days**: Monday through Saturday
- **Time slots**: 9:00 AM to 6:00 PM (15-minute intervals)

### Customizing Settings

1. Go to **Admin Dashboard** → **Settings** tab
2. Modify:
   - Facility name
   - Cutoff hours (advance notice required)
   - Available days of the week
   - Time slots (one per line)

## Data Storage

The application stores data in local files:
- `signups.csv` - All athlete signups
- `settings.json` - System configuration

## Deployment Options

### Local Network Access
To make the portal accessible to other devices on your network:
```bash
python -m streamlit run app.py --server.address 0.0.0.0
```

### Cloud Deployment
The application can be deployed to:
- **Streamlit Cloud** (free tier available)
- **Heroku**
- **AWS/Azure/GCP**
- **Any Python hosting service**

### For Streamlit Cloud Deployment:
1. Push your code to GitHub
2. Connect your GitHub repository to Streamlit Cloud
3. Deploy with the command: `python -m streamlit run app.py`

## Security Notes

- **Change the admin password** in `app.py` (line with `admin_password == "admin123"`)
- For production use, implement proper authentication
- Consider adding email notifications for signups
- Regular backups of `signups.csv` and `settings.json` are recommended

## File Structure

```
Bullpen_Signup/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── signups.csv        # Generated: athlete signups
└── settings.json      # Generated: system settings
```

## Support

For issues or questions:
1. Check the console output for error messages
2. Ensure all dependencies are installed correctly
3. Verify file permissions for data storage

## Future Enhancements

Potential features to add:
- Email notifications
- SMS reminders
- Payment integration
- Calendar integration
- Mobile app
- Advanced reporting
- User accounts and profiles
