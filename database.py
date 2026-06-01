import sqlite3

DB_NAME = "hospital.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Patients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        guardian_phone TEXT NOT NULL,
        surgery_type TEXT NOT NULL,
        doctor_phone TEXT NOT NULL
    )
    """)

    # Responses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS responses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        message TEXT,
        risk_level TEXT,
        recovery_score INTEGER,
        medication TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    conn.commit()
    conn.close()


# =====================================
# PATIENT FUNCTIONS
# =====================================

def add_patient(
    name,
    phone,
    guardian_phone,
    surgery_type,
    doctor_phone
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients
    (
        name,
        phone,
        guardian_phone,
        surgery_type,
        doctor_phone
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        name,
        phone,
        guardian_phone,
        surgery_type,
        doctor_phone
    ))

    conn.commit()
    conn.close()


def get_all_patients():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients"
    )

    patients = cursor.fetchall()

    conn.close()

    return patients


def get_patient_by_phone(phone):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE phone=?",
        (phone,)
    )

    patient = cursor.fetchone()

    conn.close()

    return patient


# =====================================
# RESPONSE FUNCTIONS
# =====================================

def add_response(
    patient_id,
    message,
    risk_level,
    recovery_score
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO responses
    (
        patient_id,
        message,
        risk_level,
        recovery_score,
        medication
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        patient_id,
        message,
        risk_level,
        recovery_score,
        ""
    ))

    conn.commit()
    conn.close()


def get_all_responses():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        responses.id,
        patients.name,
        responses.message,
        responses.risk_level,
        responses.recovery_score,
        responses.medication,
        responses.timestamp

    FROM responses

    JOIN patients
    ON responses.patient_id = patients.id

    ORDER BY responses.timestamp DESC
    """)

    responses = cursor.fetchall()

    conn.close()

    return responses


def update_medication(
    response_id,
    medication
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE responses
    SET medication = ?
    WHERE id = ?
    """,
    (
        medication,
        response_id
    ))

    conn.commit()
    conn.close()


# =====================================
# DASHBOARD STATS
# =====================================

def get_dashboard_stats():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM patients"
    )
    total_patients = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM responses
    WHERE risk_level='High Risk'
    """)
    high_risk = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM responses
    WHERE risk_level='Mild Concern'
    """)
    mild_risk = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM responses
    WHERE risk_level='Normal'
    """)
    normal = cursor.fetchone()[0]

    conn.close()

    return {
        "total_patients": total_patients,
        "high_risk": high_risk,
        "mild_risk": mild_risk,
        "normal": normal
    }

def get_patients_without_response():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM patients
    WHERE id NOT IN (
        SELECT DISTINCT patient_id
        FROM responses
    )
    """)

    patients = cursor.fetchall()

    conn.close()

    return patients