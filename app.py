from flask import (
    Flask,
    render_template,
    request,
    redirect
)

from database import (
    get_all_responses,
    update_medication,
    get_dashboard_stats
)

from database import (
    init_db,
    add_patient,
    get_all_patients,
    get_patient_by_phone,
    add_response
)

from ai_analyzer import analyze_symptoms
from database import get_patients_without_response
from dotenv import load_dotenv
from twilio.rest import Client

import os

app = Flask(__name__)

# ==========================
# LOAD ENV VARIABLES
# ==========================

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

# ==========================
# HOME
# ==========================

@app.route("/")
def home():
    return render_template("home.html")


# ==========================
# ADMIN DASHBOARD
# ==========================

@app.route("/admin")
def admin():
    patients = get_all_patients()

    return render_template(
        "dashboard.html",
        patients=patients
    )


# ==========================
# REGISTER PATIENT
# ==========================

@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    phone = request.form["phone"]
    guardian_phone = request.form["guardian_phone"]
    surgery_type = request.form["surgery_type"]
    doctor_phone = request.form["doctor_phone"]

    add_patient(
        name,
        phone,
        guardian_phone,
        surgery_type,
        doctor_phone
    )

    return redirect("/admin")


# ==========================
# SEND DAILY CHECKINS
# ==========================

@app.route("/send_checkins")
def send_checkins():

    patients = get_all_patients()

    for patient in patients:

        name = patient[1]
        phone = patient[2]

        try:

            client.messages.create(
                body=f"Hi {name}, how are you feeling today after discharge? Please describe any symptoms.",
                from_=twilio_number,
                to=f"whatsapp:+91{phone}"
            )

            print(f"Message sent to {name}")

        except Exception as e:

            print("Twilio Error:", e)

    return redirect("/admin")


# ==========================
# WHATSAPP WEBHOOK
# ==========================

@app.route("/webhook", methods=["POST"])
def webhook():

    print("WEBHOOK HIT")

    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")

    print("Message received:", incoming_msg)
    print("From:", sender)

    phone = sender.replace("whatsapp:+91", "")

    patient = get_patient_by_phone(phone)

    if patient:

        analysis = analyze_symptoms(incoming_msg)

        risk_level = analysis["risk_level"]
        recovery_score = analysis["recovery_score"]

        add_response(
            patient[0],
            incoming_msg,
            risk_level,
            recovery_score
        )

        print("Risk Level:", risk_level)
        print("Recovery Score:", recovery_score)

        # ==========================
        # AUTO REPLY TO PATIENT
        # ==========================

        if risk_level == "Normal":

            reply_message = """
✅ Thank you for the update.

Your recovery appears normal.

Please continue following your doctor's instructions.
"""

        elif risk_level == "Mild Concern":

            reply_message = """
⚠️ Your symptoms have been recorded.

A doctor will review your condition.

If symptoms worsen, please contact the hospital.
"""

        else:

            reply_message = """
🚨 HIGH RISK ALERT

Your symptoms may require immediate medical attention.

Your doctor has been notified.

Please seek emergency help if required.
"""

        try:

            client.messages.create(
                body=reply_message,
                from_=twilio_number,
                to=sender
            )

            print("Patient auto-reply sent")

        except Exception as e:

            print("Patient reply error:", e)

        # ==========================
        # HIGH RISK DOCTOR ALERT
        # ==========================

        if risk_level == "High Risk":

            try:

                client.messages.create(
                    body=f"""
🚨 HIGH RISK PATIENT ALERT

Patient: {patient[1]}

Response:
{incoming_msg}

Immediate review required.
""",
                    from_=twilio_number,
                    to=f"whatsapp:+91{patient[5]}"
                )

                print("Doctor alert sent")

            except Exception as e:

                print("Doctor alert error:", e)

    else:

        print("Patient NOT found in database")

    return "OK", 200

# ==========================
# RUN APP
# ==========================
# ==========================
# DOCTOR DASHBOARD
# ==========================

@app.route("/doctor")
def doctor():

    responses = get_all_responses()
    stats = get_dashboard_stats()

    return render_template(
        "doctor.html",
        responses=responses,
        stats=stats
    )


# ==========================
# PRESCRIBE MEDICATION
# ==========================

@app.route("/prescribe", methods=["POST"])
def prescribe():

    response_id = request.form["response_id"]
    medication = request.form["medication"]

    update_medication(
        response_id,
        medication
    )

    return redirect("/doctor")

# ==========================
# GUARDIAN ALERTS
# ==========================

@app.route("/check_missing_responses")
def check_missing_responses():

    patients = get_patients_without_response()

    for patient in patients:

        try:

            client.messages.create(
                body=f"""
ALERT

Patient {patient[1]} has not responded to today's recovery check-in.

Please contact the patient immediately.
""",
                from_=twilio_number,
                to=f"whatsapp:+91{patient[3]}"
            )

            print(
                f"Guardian alert sent for {patient[1]}"
            )

        except Exception as e:

            print(
                "Guardian alert error:",
                e
            )

    return redirect("/admin")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)