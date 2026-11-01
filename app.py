
import os
import sqlite3
from functools import wraps
from datetime import date
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "clinic.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is not set")
app.config["DATABASE"] = DB_PATH


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('patient','doctor','admin')),
        active INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        fees REAL NOT NULL DEFAULT 300,
        available INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        reason TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES users(id),
        FOREIGN KEY(doctor_id) REFERENCES doctors(id)
    );
    """)

    # Create admin if missing
    admin = conn.execute(
        "SELECT id FROM users WHERE email=?",
        ("admin@smartclinic.com",)
    ).fetchone()

    if not admin:
        conn.execute("""
            INSERT INTO users(name,email,password_hash,role)
            VALUES(?,?,?,?)
        """, (
            "Clinic Admin",
            "admin@smartclinic.com",
            generate_password_hash("Admin@123"),
            "admin"
        ))

    # Create demo doctors if missing
    demo_doctors = [
        (
            "Dr. Aanya Sharma",
            "doctor@smartclinic.com",
            "Doctor@123",
            "General Physician",
            400
        ),
        (
            "Dr. Rohan Mehta",
            "doctor2@smartclinic.com",
            "Doctor@123",
            "Dermatologist",
            500
        )
    ]

    for name, email, password, specialization, fees in demo_doctors:

        existing = conn.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if not existing:

            cursor = conn.execute("""
                INSERT INTO users(name,email,password_hash,role)
                VALUES(?,?,?,'doctor')
            """, (
                name,
                email,
                generate_password_hash(password)
            ))

            conn.execute("""
                INSERT INTO doctors(
                    user_id,name,specialization,fees,available
                )
                VALUES(?,?,?,?,1)
            """, (
                cursor.lastrowid,
                name,
                specialization,
                fees
            ))

    conn.commit()

    # --------------------------------------------------
    # DOCTOR AVAILABILITY DIAGNOSTIC
    # --------------------------------------------------

    rows = conn.execute(
        "SELECT id, name, available FROM doctors"
    ).fetchall()

    print("\n--- DOCTOR AVAILABILITY CHECK ---")

    for row in rows:
        print(dict(row))

    print("---------------------------------\n")

    conn.close()


# --------------------------------------------------
# AUTHENTICATION DECORATORS
# --------------------------------------------------

def login_required(view_func):

    @wraps(view_func)
    def protected_view(*args, **kwargs):

        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))

        return view_func(*args, **kwargs)

    return protected_view


def role_required(required_role):

    def check_role(view_func):

        @wraps(view_func)
        def protected_view(*args, **kwargs):

            if not session.get("user_id"):
                flash("Please login first.", "warning")
                return redirect(url_for("login"))

            if session.get("role") != required_role:
                abort(403)

            return view_func(*args, **kwargs)

        return protected_view

    return check_role


# --------------------------------------------------
# GLOBAL TEMPLATE DATA
# --------------------------------------------------

@app.context_processor
def inject_user():

    return {
        "current_user": session.get("name"),
        "current_role": session.get("role")
    }


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def index():

    conn = get_db()

    doctors = conn.execute("""
        SELECT * FROM doctors
        WHERE available=1
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template("index.html", doctors=doctors)


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 8:
            flash(
                "Enter all details. Password must be at least 8 characters.",
                "danger"
            )
            return redirect(url_for("register"))

        conn = get_db()

        try:

            conn.execute("""
                INSERT INTO users(name,email,password_hash,role)
                VALUES(?,?,?,'patient')
            """, (
                name,
                email,
                generate_password_hash(password)
            ))

            conn.commit()

            flash("Registration successful. Please log in.", "success")

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash("This email is already registered.", "danger")

        finally:
            conn.close()

    return render_template("register.html")


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute("""
            SELECT * FROM users
            WHERE email=? AND active=1
        """, (email,)).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password_hash"], password
        ):

            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        flash("Invalid email/password or inactive account.", "danger")

    return render_template("login.html")


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()
    flash("You have been logged out.", "success")

    return redirect(url_for("index"))


# --------------------------------------------------
# DASHBOARD REDIRECTION
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    dashboards = {
        "admin": "admin_dashboard",
        "doctor": "doctor_dashboard",
        "patient": "patient_dashboard"
    }

    endpoint = dashboards.get(session.get("role"))

    if not endpoint:
        abort(403)

    return redirect(url_for(endpoint))


# --------------------------------------------------
# PATIENT DASHBOARD
# --------------------------------------------------

@app.route("/patient-dashboard")
@role_required("patient")
def patient_dashboard():

    conn = get_db()

    appointments = conn.execute("""
        SELECT a.*, d.name AS doctor_name,
               d.specialization
        FROM appointments a
        JOIN doctors d ON d.id=a.doctor_id
        WHERE a.patient_id=?
        ORDER BY a.id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "patient_dashboard.html",
        appointments=appointments
    )


# --------------------------------------------------
# DOCTOR DIRECTORY
# --------------------------------------------------

@app.route("/doctors")
@login_required
def doctors():

    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM doctors
        WHERE available=1
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template("doctors.html", doctors=rows)


# --------------------------------------------------
# BOOK APPOINTMENT
# --------------------------------------------------

@app.route("/book/<int:doctor_id>", methods=["GET", "POST"])
@role_required("patient")
def book(doctor_id):

    conn = get_db()

    doctor = conn.execute("""
        SELECT * FROM doctors
        WHERE id=? AND available=1
    """, (doctor_id,)).fetchone()

    if not doctor:
        conn.close()
        abort(404)

    if request.method == "POST":

        appointment_date = request.form.get(
            "appointment_date", ""
        )

        appointment_time = request.form.get(
            "appointment_time", ""
        )

        reason = request.form.get("reason", "").strip()

        if not appointment_date or not appointment_time:

            flash("Please select appointment date and time.", "danger")

        elif appointment_date < date.today().isoformat():

            flash("Please select a future date.", "danger")

        else:

            conflict = conn.execute("""
                SELECT id FROM appointments
                WHERE doctor_id=?
                AND appointment_date=?
                AND appointment_time=?
                AND status IN ('Pending','Approved')
            """, (
                doctor_id,
                appointment_date,
                appointment_time
            )).fetchone()

            if conflict:

                flash("This time slot is already booked or requested.", "danger")

            else:

                conn.execute("""
                    INSERT INTO appointments(
                        patient_id, doctor_id,
                        appointment_date, appointment_time, reason
                    )
                    VALUES(?,?,?,?,?)
                """, (
                    session["user_id"],
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    reason
                ))

                conn.commit()
                conn.close()

                flash(
                    "Appointment request submitted. Status: Pending.",
                    "success"
                )

                return redirect(url_for("patient_dashboard"))

    conn.close()

    return render_template("book.html", doctor=doctor)


# --------------------------------------------------
# CANCEL APPOINTMENT
# --------------------------------------------------

@app.route("/cancel/<int:appointment_id>", methods=["POST"])
@role_required("patient")
def cancel(appointment_id):

    conn = get_db()

    conn.execute("""
        UPDATE appointments
        SET status='Cancelled'
        WHERE id=? AND patient_id=? AND status='Pending'
    """, (
        appointment_id,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    flash("Pending appointment cancelled, if eligible.", "success")

    return redirect(url_for("patient_dashboard"))


# --------------------------------------------------
# DOCTOR DASHBOARD
# --------------------------------------------------

@app.route("/doctor-dashboard")
@role_required("doctor")
def doctor_dashboard():

    conn = get_db()

    doctor = conn.execute("""
        SELECT * FROM doctors
        WHERE user_id=?
    """, (session["user_id"],)).fetchone()

    if not doctor:

        conn.close()
        flash("Doctor profile not found.", "danger")

        return redirect(url_for("logout"))

    appointments = conn.execute("""
        SELECT a.*, u.name AS patient_name,
               u.email AS patient_email
        FROM appointments a
        JOIN users u ON u.id=a.patient_id
        WHERE a.doctor_id=?
        ORDER BY a.appointment_date DESC,
                 a.appointment_time DESC
    """, (doctor["id"],)).fetchall()

    conn.close()

    return render_template(
        "doctor_dashboard.html",
        doctor=doctor,
        appointments=appointments
    )


# --------------------------------------------------
# DOCTOR UPDATE APPOINTMENT
# --------------------------------------------------

@app.route(
    "/doctor/appointment/<int:appointment_id>/<action>",
    methods=["POST"]
)
@role_required("doctor")
def doctor_update_appointment(appointment_id, action):

    actions = {
        "approve": "Approved",
        "reject": "Rejected",
        "complete": "Completed"
    }

    if action not in actions:
        abort(400)

    conn = get_db()

    doctor = conn.execute("""
        SELECT id FROM doctors
        WHERE user_id=?
    """, (session["user_id"],)).fetchone()

    if doctor:

        conn.execute("""
            UPDATE appointments
            SET status=?
            WHERE id=? AND doctor_id=? AND status='Pending'
        """, (
            actions[action],
            appointment_id,
            doctor["id"]
        ))

        conn.commit()

    conn.close()

    flash("Appointment status updated, if eligible.", "success")

    return redirect(url_for("doctor_dashboard"))


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.route("/admin-dashboard")
@role_required("admin")
def admin_dashboard():

    conn = get_db()

    stats = {
        "patients": conn.execute(
            "SELECT COUNT(*) FROM users WHERE role='patient'"
        ).fetchone()[0],

        "doctors": conn.execute(
            "SELECT COUNT(*) FROM doctors"
        ).fetchone()[0],

        "appointments": conn.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0],

        "pending": conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE status='Pending'"
        ).fetchone()[0]
    }

    doctor_rows = conn.execute("""
        SELECT d.*, u.email
        FROM doctors d
        LEFT JOIN users u ON u.id=d.user_id
        ORDER BY d.id DESC
    """).fetchall()

    appointment_rows = conn.execute("""
        SELECT a.*, p.name AS patient_name,
               d.name AS doctor_name
        FROM appointments a
        JOIN users p ON p.id=a.patient_id
        JOIN doctors d ON d.id=a.doctor_id
        ORDER BY a.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        doctors=doctor_rows,
        appointments=appointment_rows
    )


# --------------------------------------------------
# ADMIN ADD DOCTOR
# --------------------------------------------------

@app.route("/admin/add-doctor", methods=["POST"])
@role_required("admin")
def add_doctor():

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    specialization = request.form.get(
        "specialization", ""
    ).strip()

    password = request.form.get("password", "")

    try:

        fees = float(request.form.get("fees", "300"))

        if fees < 0:
            raise ValueError()

    except ValueError:

        flash("Enter valid consultation fees.", "danger")

        return redirect(url_for("admin_dashboard"))

    if not name or not email or not specialization or len(password) < 8:

        flash("Complete all fields. Password must be at least 8 characters.", "danger")

        return redirect(url_for("admin_dashboard"))

    conn = get_db()

    try:

        cursor = conn.execute("""
            INSERT INTO users(name,email,password_hash,role)
            VALUES(?,?,?,'doctor')
        """, (
            name,
            email,
            generate_password_hash(password)
        ))

        conn.execute("""
            INSERT INTO doctors(user_id,name,specialization,fees)
            VALUES(?,?,?,?)
        """, (
            cursor.lastrowid,
            name,
            specialization,
            fees
        ))

        conn.commit()

        flash("Doctor added successfully.", "success")

    except sqlite3.IntegrityError:

        flash("Email already exists.", "danger")

    finally:

        conn.close()

    return redirect(url_for("admin_dashboard"))


# --------------------------------------------------
# ADMIN TOGGLE DOCTOR
# --------------------------------------------------

@app.route(
    "/admin/doctor/<int:doctor_id>/toggle",
    methods=["POST"]
)
@role_required("admin")
def admin_toggle_doctor(doctor_id):

    conn = get_db()

    row = conn.execute("""
        SELECT available FROM doctors
        WHERE id=?
    """, (doctor_id,)).fetchone()

    if row:

        new_value = 0 if row["available"] else 1

        conn.execute("""
            UPDATE doctors SET available=?
            WHERE id=?
        """, (new_value, doctor_id))

        conn.commit()

        flash("Doctor availability updated.", "success")

    else:

        flash("Doctor not found.", "danger")

    conn.close()

    return redirect(url_for("admin_dashboard"))


# --------------------------------------------------
# ADMIN CANCEL APPOINTMENT
# --------------------------------------------------

@app.route(
    "/admin/appointment/<int:appointment_id>/cancel",
    methods=["POST"]
)
@role_required("admin")
def admin_cancel_appointment(appointment_id):

    conn = get_db()

    conn.execute("""
        UPDATE appointments
        SET status='Cancelled'
        WHERE id=?
        AND status IN ('Pending','Approved')
    """, (appointment_id,))

    conn.commit()
    conn.close()

    flash("Appointment cancelled, if eligible.", "success")

    return redirect(url_for("admin_dashboard"))


# --------------------------------------------------
# ERROR HANDLERS
# --------------------------------------------------

@app.errorhandler(403)
def forbidden(error):

    return render_template(
        "error.html",
        code=403,
        message="You do not have permission to view this page."
    ), 403


@app.errorhandler(404)
def not_found(error):

    return render_template(
        "error.html",
        code=404,
        message="The page you requested was not found."
    ), 404


@app.errorhandler(500)
def server_error(error):

    return render_template(
        "error.html",
        code=500,
        message="Something went wrong. Please try again."
    ), 500


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------
init_db()

if __name__ == "__main__":
    print("Smart Clinic database initialized.")
    print("Starting Smart Clinic Appointment System...")

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )