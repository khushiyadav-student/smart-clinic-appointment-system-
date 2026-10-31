

import os
import sqlite3
from datetime import date, datetime
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, g
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/")
def home():
    return render_template("index.html")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 8:
            flash("Please enter valid details. Password must be 8 characters.")
            return redirect(url_for("register"))

        db = get_db()

        try:
            db.execute(
                """
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, 'patient')
                """,
                (name, email, generate_password_hash(password))
            )
            db.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email already registered.")

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]

            flash("Login successful!")
            return redirect(url_for("doctors"))

        flash("Invalid email or password.")

    return render_template("login.html")
@app.route("/doctors")
def doctors():
    db = get_db()

    doctors_list = db.execute(
        "SELECT * FROM doctors WHERE available = 1"
    ).fetchall()

    return render_template(
        "doctors.html",
        doctors=doctors_list
    )
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))
@app.route("/appointments")
@login_required
def appointments():
    db = get_db()

    appointments_list = db.execute("""
        SELECT appointments.*, doctors.name AS doctor_name,
               doctors.specialization
        FROM appointments
        JOIN doctors ON appointments.doctor_id = doctors.id
        WHERE appointments.patient_id = ?
        ORDER BY appointments.appointment_date DESC
    """, (session["user_id"],)).fetchall()

    return render_template(
        "appointments.html",
        appointments=appointments_list
    )
@app.route("/book/<int:doctor_id>", methods=["GET", "POST"])
@login_required
def book_appointment(doctor_id):
    db = get_db()

    doctor = db.execute(
        "SELECT * FROM doctors WHERE id = ? AND available = 1",
        (doctor_id,)
    ).fetchone()

    if doctor is None:
        flash("Doctor not found.")
        return redirect(url_for("doctors"))

    if request.method == "POST":
        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")

        try:
            selected_date = date.fromisoformat(appointment_date)
            datetime.strptime(appointment_time, "%H:%M")

            if selected_date < date.today():
                flash("Please select a future date.")
                return redirect(url_for("book_appointment", doctor_id=doctor_id))

            db.execute("BEGIN IMMEDIATE")

            existing = db.execute("""
                SELECT id FROM appointments
                WHERE doctor_id = ?
                AND appointment_date = ?
                AND appointment_time = ?
                AND status = 'Booked'
            """, (doctor_id, appointment_date, appointment_time)).fetchone()

            if existing:
                db.rollback()
                flash("This slot is already booked.")
            else:
                db.execute("""
                    INSERT INTO appointments
                    (patient_id, doctor_id, appointment_date, appointment_time)
                    VALUES (?, ?, ?, ?)
                """, (
                    session["user_id"],
                    doctor_id,
                    appointment_date,
                    appointment_time
                ))
                db.commit()
                flash("Appointment booked successfully!")
                return redirect(url_for("appointments"))

        except (ValueError, TypeError):
            db.rollback()
            flash("Please enter a valid date and time.")

    return render_template(
    "book.html",
    doctor=doctor,
    today=date.today().isoformat()
)
@app.route("/cancel/<int:appointment_id>", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    db = get_db()

    result = db.execute("""
        UPDATE appointments
        SET status = 'Cancelled'
        WHERE id = ?
        AND patient_id = ?
        AND status = 'Booked'
    """, (appointment_id, session["user_id"]))

    db.commit()

    if result.rowcount:
        flash("Appointment cancelled successfully.")
    else:
        flash("Appointment could not be cancelled.")

    return redirect(url_for("appointments"))
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "replace-this-for-local-development"
)
app.config["DATABASE"] = os.path.join(
    app.root_path, "clinic.db"
)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'patient'
        );

        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1,
            fees REAL NOT NULL DEFAULT 500,
            user_id INTEGER UNIQUE,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Booked',
            FOREIGN KEY(patient_id) REFERENCES users(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        );

        CREATE INDEX IF NOT EXISTS idx_appointments_slot
        ON appointments(doctor_id, appointment_date, appointment_time);
    """)

    # Safely migrate existing databases
    user_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(users)")
    }

    if "role" not in user_columns:
        db.execute("""
            ALTER TABLE users
            ADD COLUMN role TEXT NOT NULL DEFAULT 'patient'
        """)

    doctor_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(doctors)")
    }

    if "fees" not in doctor_columns:
        db.execute("""
            ALTER TABLE doctors
            ADD COLUMN fees REAL NOT NULL DEFAULT 500
        """)

    if "user_id" not in doctor_columns:
        db.execute("""
            ALTER TABLE doctors
            ADD COLUMN user_id INTEGER REFERENCES users(id)
        """)

    db.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_doctors_user_id
        ON doctors(user_id)
    """)

    count = db.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    if count == 0:
        db.executemany(
            """INSERT INTO doctors
               (name, specialization, fees)
               VALUES (?, ?, ?)""",
            [
                ("Dr. Aditi Sharma", "General Physician", 500),
                ("Dr. Rahul Verma", "Dermatologist", 700),
                ("Dr. Neha Patel", "Pediatrician", 600),
                ("Dr. Arjun Mehta", "Cardiologist", 1000),
                ("Dr. Priya Singh", "Gynecologist", 800),
            ],
        )

    db.commit()   
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)