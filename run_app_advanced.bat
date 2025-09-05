@echo off
echo Starting Bullpen Signup Portal...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking Streamlit installation...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Streamlit not found. Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

echo.
echo Starting the application...
echo The application will open in your default web browser.
echo.
echo To stop the application, press Ctrl+C in this window
echo.

python -m streamlit run app.py

echo.
echo Application stopped.
pause
