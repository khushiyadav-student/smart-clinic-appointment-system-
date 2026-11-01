# 🏥 Smart Clinic Appointment System

A web-based clinic appointment management application developed using Python Flask, HTML, CSS, JavaScript and SQLite.

## 📌 Project Overview

The Smart Clinic Appointment System is designed to simplify appointment booking and management by connecting patients, doctors and administrators through a centralized digital platform.

## 🎯 Problem Statement

Traditional clinic appointment systems involve manual booking, long waiting queues, scheduling conflicts and difficulty tracking appointment status. This project aims to make clinic appointment management easier and more organized.

## ✨ Key Features

### 👤 Patient Module
- Patient registration and login
- View available doctors
- Book clinic appointments
- View appointment status
- Cancel appointments

### 🩺 Doctor Module
- Dedicated doctor dashboard
- View appointment requests
- Approve or reject appointments
- Manage appointment workflow

### 🔐 Admin Module
- Admin authentication
- View dashboard statistics
- Add and manage doctors
- Update doctor availability
- Monitor appointments

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, Flask |
| Database | SQLite |
| Templates | Jinja2 |
| Security | Werkzeug |
| IDE | Visual Studio Code |
| Version Control | Git and GitHub |

## 📂 Project Structure

```text
Smart-Clinic/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── patient_dashboard.html
    ├── doctors.html
    ├── book.html
    ├── doctor_dashboard.html
    ├── admin_dashboard.html
    └── error.html
```

## ⚙️ Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/khushiyadav-student/smart-clinic-appointment-system-.git
```

2. Open the project folder:

```bash
cd smart-clinic-appointment-system-
```

3. Create a virtual environment:

```bash
python -m venv .venv
```

4. Activate it on Windows:

```bash
.venv\Scripts\activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Set the Flask secret key in PowerShell:

```powershell
$env:SECRET_KEY="your-local-secret-key"
```

7. Run the application:

```bash
python app.py
```

8. Open your browser:

```text
http://127.0.0.1:5000
```

## 🔑 Demo Login Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@smartclinic.com | Admin@123 |
| Doctor | doctor@smartclinic.com | Doctor@123 |
| Doctor | doctor2@smartclinic.com | Doctor@123 |

Patients can register through the registration page.

*Demo credentials are for local academic testing only. Change default credentials before public deployment.*

## 🗄️ Database

The application uses SQLite to store patient, doctor and appointment information.

## 🚀 Future Enhancements

- Email and SMS appointment notifications
- Doctor availability calendar
- Appointment history and reports
- Online payment integration
- Improved security and deployment

## 🎓 Academic Project

- **Project Name:** Smart Clinic Appointment System
- **Developer:** Khushi Yadav
- **Course:** Master of Computer Applications (MCA)
- **Institution:** Avantika University
- **Version:** 1.0

## ⚠️ Disclaimer

This project is developed as an academic prototype for learning and demonstration purposes. It is not intended for production healthcare use.

---

⭐ Explore the repository: [Smart Clinic Appointment System](https://github.com/khushiyadav-student/smart-clinic-appointment-system-)