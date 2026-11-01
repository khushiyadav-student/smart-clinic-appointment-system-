# Smart Clinic Appointment System

A beginner-friendly Flask + SQLite full-stack prototype with three role-based portals.

## Features
- Patient registration/login and appointment booking/cancellation
- Doctor dashboard with approve, reject and complete actions
- Admin dashboard with clinic statistics, doctor management and appointment oversight
- SQLite database auto-created on first run
- Responsive interface

## Run locally (Windows PowerShell)
1. Extract this ZIP.
2. Open the extracted `Smart_Clinic_Prototype` folder in VS Code.
3. Open Terminal and run:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```
4. Open http://127.0.0.1:5000

## Demo accounts
- Admin: `admin@smartclinic.com` / `Admin@123`
- Doctor: `doctor@smartclinic.com` / `Doctor@123`
- Second doctor: `doctor2@smartclinic.com` / `Doctor@123`
- Patient: create one through Register.

## Notes
This is an academic prototype, not a production medical system. Change `SECRET_KEY`, add CSRF protection, stronger validation, secure deployment settings and privacy controls before any real-world use. Do not enter real patient medical information.
