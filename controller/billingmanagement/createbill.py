from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

createbillbp = Blueprint('createbillbp', __name__)

@createbillbp.route('/billing/createbill', methods=['POST'])
def createbillfn():
    db = get_db_connection()
    billing_collection = db['billing']
    patients_collection = db['patients']
    doctors_collection = db['doctors']

    # Required inputs
    patientemailid = str(request.form.get('patientemailid'))
    doctoremailid = request.form.get('doctoremailid')
    purpose = str(request.form.get('purpose'))

    # Optional inputs from frontend
    rooms = request.form.get('rooms', '').strip().lower()
    treatmenttype = request.form.get('treatmenttype', '').strip().lower()
    treatmentduration = safe_int(request.form.get('treatmentduration'))

    # Charges must come from frontend
    room_charge = safe_float(request.form.get('room_charge'))
    treatment_charge = safe_float(request.form.get('treatment_charge'))
    medicine_charge = safe_float(request.form.get('medicine_charge'))
    lab_charge = safe_float(request.form.get('lab_charge'))
    other_charges = safe_float(request.form.get('other_charges'))
    fees_amount = safe_float(request.form.get('fees_amount'))
    discount_percent = safe_float(request.form.get('discount_percent'))
    insurance_provider = request.form.get('insurance_provider')
    insurance_coverage_percent = safe_float(request.form.get('insurance_coverage_percent'))
    payment_method = request.form.get('payment_method', 'cash')
    notes = request.form.get('notes', '')
    created_by = request.form.get('created_by', 'system')

    # Fetch patient
    patient = patients_collection.find_one({"email": patientemailid})
    if not patient:
        return jsonify({"status": False, "message": "Patient not found"}), 404

    # Fetch doctor only if provided
    doctor = None
    if doctoremailid:
        doctor = doctors_collection.find_one({"email": str(doctoremailid)})

    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    bill_id = str(uuid.uuid4())

    # Billing calculation using only frontend values
    gross_total = room_charge + treatment_charge + medicine_charge + lab_charge + other_charges + fees_amount
    discount_amount = (discount_percent / 100) * gross_total
    after_discount = gross_total - discount_amount
    insurance_coverage_amount = (insurance_coverage_percent / 100) * after_discount
    final_amount_payable = after_discount - insurance_coverage_amount

    # Create billing document
    bill_data = {
        "bill_id": bill_id,
        "created_at": now.isoformat(),
        "status": "pending",
        "purpose": purpose,

        # Patient Info
        "patient_uid": patient["uid"],
        "patient_name": f"{patient['firstname']} {patient['lastname']}",
        "patient_email": patientemailid,
        "patient_phone": patient["phonenumber"],
        "patient_gender": patient.get("gender"),
        "patient_age": patient.get("age"),

        # Doctor Info (optional)
        "doctor_uid": doctor.get("uid") if doctor else None,
        "doctor_name": doctor.get("fullname") if doctor else None,
        "doctor_email": doctoremailid if doctor else None,
        "doctor_phone": doctor.get("phonenumber") if doctor else None,
        "department": doctor.get("specialization") if doctor else None,
        "qualification": doctor.get("qualification") if doctor else None,
        "license_number": doctor.get("license_number") if doctor else None,

        # Treatment Info
        "room_type": rooms,
        "treatment_type": treatmenttype,
        "treatment_duration_days": treatmentduration,
        "room_charge": room_charge,
        "treatment_charge": treatment_charge,
        "medicine_charge": medicine_charge,
        "lab_charge": lab_charge,
        "other_charges": other_charges,
        "fees_amount": fees_amount,
        "gross_total": gross_total,

        # Adjustments
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "insurance_provider": insurance_provider,
        "insurance_coverage_percent": insurance_coverage_percent,
        "insurance_coverage_amount": insurance_coverage_amount,
        "final_amount_payable": final_amount_payable,
        "final_amount": final_amount_payable,

        # Payment Info
        "payment_method": payment_method,
        "payment_status": "pending",

        # Audit
        "created_by": created_by,
        "notes": notes
    }

    billing_collection.insert_one(bill_data)

    # Email notification
    email_subject = f"Hospital Billing Confirmation - Bill ID {bill_id}"
    email_body = f"""
Dear {patient['firstname']},

Your bill has been generated.

Details:
- Bill ID: {bill_id}
- Purpose: {purpose}
- Room: {rooms or 'N/A'}
- Treatment: {treatmenttype or 'N/A'} for {treatmentduration} day(s)
- Room Charges: ₹{room_charge}
- Treatment Charges: ₹{treatment_charge}
- Medicines: ₹{medicine_charge}
- Lab Charges: ₹{lab_charge}
- Other Charges: ₹{other_charges}
- Fees: ₹{fees_amount}
- Discount: {discount_percent}% (-₹{discount_amount})
- Insurance: {insurance_coverage_percent}% (-₹{insurance_coverage_amount})
- Final Amount Payable: ₹{final_amount_payable}
"""

    if doctor:
        email_body += f"\n- Doctor: {doctor['fullname']} ({doctor.get('specialization', 'N/A')})"

    email_body += f"\n\nPlease visit the billing counter or use online payment via {payment_method}.\n\nRegards,\nHospital Admin"

    email_sender(patientemailid, email_subject, email_body)

    generatelogs('success', f"Billing created for {patientemailid} by {doctoremailid if doctoremailid else 'N/A'} with Bill ID {bill_id}", 'billingops/createbill.py')

    return jsonify({
        "status": True,
        "message": "Bill created successfully",
        "bill_id": bill_id,
        "gross_total": gross_total,
        "final_amount": final_amount_payable
    }), 200
