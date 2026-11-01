# 🏥 Smart Clinic Appointment System

A web-based clinic appointment management application developed using Python Flask and SQLite. The system simplifies appointment booking and management by connecting patients, doctors, and administrators through dedicated dashboards.

## 📌 Project Overview

The Smart Clinic Appointment System is designed to reduce manual appointment scheduling, minimize waiting time, and improve coordination between patients and clinic staff.

Patients can register, log in, view available doctors, and request appointments. Doctors can manage appointment requests, while administrators can manage doctors and monitor clinic activities.

## 🎯 Problem Statement

Traditional clinic appointment systems often involve manual booking, long waiting queues, scheduling conflicts, and difficulty tracking appointment status.

This project provides a centralized digital platform to make clinic appointment management easier, faster, and more organized.

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
- Mark appointments as completed
- Manage appointment workflow

### 🔐 Admin Module
- Admin authentication
- View dashboard statistics
- Add and manage doctors
- Update doctor availability
- Monitor and cancel appointments

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database management |
| HTML5 | Web page structure |
| CSS3 | Styling and layout |
| Jinja2 | Dynamic templates |
| Werkzeug | Password hashing |

## 📂 Project Structure

```text
Smart-Clinic/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
│
├── static/
│   └── style.css
│
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

### 1. Clone the repository

```bash
git clone https://github.com/khushiyadav-student/smart-clinic-appointment-system-.git
```

### 2. Navigate to project folder

```bash
cd smart-clinic-appointment-system-
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

### 7. Open in browser

```text
http://127.0.0.1:5000
```

## 🔑 Demo Login Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@smartclinic.com | Admin@123 |
| Doctor | doctor@smartclinic.com | Doctor@123 |
| Doctor | doctor2@smartclinic.com | Doctor@123 |

Patients can create an account through the registration page.

*Demo credentials are for local academic testing only. Change default credentials before any public deployment.*

## 🗄️ Database

The application uses SQLite for storing:

- Patient information
- Doctor information
- Appointment records
- Login and role information

## 🚀 Future Scope

- Email and SMS appointment notifications
- Online payment integration
- Doctor search and specialization filters
- Appointment reminders
- Improved security and production deployment
- Patient medical history management

## 🎓 Academic Project

**Project Name:** Smart Clinic Appointment System  
**Technology:** Python Flask and SQLite  
**Project Type:** Web-Based Application  
**Developer:** Khushi Yadav  
**GitHub:** [Smart Clinic Appointment System](https://github.com/khushiyadav-student/smart-clinic-appointment-system-)

## ⚠️ Disclaimer

This project is developed as an academic prototype for learning and demonstration purposes. It is not intended for production healthcare use.

---

⭐ If you find this project useful, feel free to explore the repository!
