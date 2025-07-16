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

createbillbp = Blueprint('createbillbp', __name__)

@createbillbp.route('/billing/createbill', methods=['POST'])
def createbillfn():
    db = get_db_connection()
    billing_collection = db['billing']
    patients_collection = db['patients']
    doctors_collection = db['doctors']

    # Extracting form data
    patientemailid = str(request.form.get('patientemailid'))
    doctoremailid = str(request.form.get('doctoremailid'))
    purpose = str(request.form.get('purpose'))
    rooms = str(request.form.get('rooms'))
    treatmenttype = str(request.form.get('treatmenttype'))
    treatmentduration = str(request.form.get('treatmentduration'))
    medicine_charge = float(request.form.get('medicine_charge', 0))
    lab_charge = float(request.form.get('lab_charge', 0))
    other_charges = float(request.form.get('other_charges', 0))
    fees_amount = float(request.form.get('fees_amount', 0))
    discount_percent = float(request.form.get('discount_percent', 0))
    insurance_provider = request.form.get('insurance_provider', None)
    insurance_coverage_percent = float(request.form.get('insurance_coverage_percent', 0))
    payment_method = request.form.get('payment_method', 'cash')
    notes = request.form.get('notes', '')
    created_by = request.form.get('created_by', 'system')

    # Fetch patient
    patient = patients_collection.find_one({"email": patientemailid})
    if not patient:
        return jsonify({"status": False, "message": "Patient not found"}), 404

    # Fetch doctor
    doctor = doctors_collection.find_one({"email": doctoremailid})
    
    # Billing calculations
    bill_id = str(uuid.uuid4())
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    room_cost = {
        "general": 1000,
        "semi-private": 2000,
        "private": 3000
    }

    treatment_costs = {
        "physiotherapy": 1500,
        "surgery": 15000,
        "consultation": 500,
        "medication": 1000
    }

    room_charge = room_cost.get(rooms.lower(), 1000) * int(treatmentduration)
    treatment_charge = treatment_costs.get(treatmenttype.lower(), 1000)

    gross_total = room_charge + treatment_charge + medicine_charge + lab_charge + other_charges + fees_amount
    discount_amount = (discount_percent / 100) * gross_total
    after_discount = gross_total - discount_amount
    insurance_coverage_amount = (insurance_coverage_percent / 100) * after_discount
    final_amount_payable = after_discount - insurance_coverage_amount

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

        # Doctor Info
        "doctor_uid": doctor["uid"],
        "doctor_name": doctor["fullname"],
        "doctor_email": doctoremailid,
        "doctor_phone": doctor.get("phonenumber"),
        "department": doctor.get("specialization"),
        "qualification": doctor.get("qualification"),
        "license_number": doctor.get("license_number"),

        # Treatment Info
        "room_type": rooms,
        "treatment_type": treatmenttype,
        "treatment_duration_days": int(treatmentduration),
        "room_charge": room_charge,
        "treatment_charge": treatment_charge,
        "medicine_charge": medicine_charge,
        "lab_charge": lab_charge,
        "other_charges": other_charges,
        "gross_total": gross_total,

        # Billing Adjustments
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "insurance_provider": insurance_provider,
        "insurance_coverage_percent": insurance_coverage_percent,
        "insurance_coverage_amount": insurance_coverage_amount,
        "final_amount_payable": final_amount_payable,
        "final_amount": final_amount_payable,

        # Payment
        "payment_method": payment_method,
        "payment_status": "pending",

        # Audit
        "created_by": created_by,
        "notes": notes
    }

    billing_collection.insert_one(bill_data)

    # Send confirmation email
    email_subject = f"Hospital Billing Confirmation - Bill ID {bill_id}"
    email_body = f"""
Dear {patient['firstname']},

Your bill has been generated.

Details:
- Bill ID: {bill_id}
- Purpose: {purpose}
- Room: {rooms}
- Treatment: {treatmenttype} for {treatmentduration} day(s)
- Room Charges: ₹{room_charge}
- Treatment Charges: ₹{treatment_charge}
- Medicines: ₹{medicine_charge}
- Lab Charges: ₹{lab_charge}
- Other Charges: ₹{other_charges}
- Discount: {discount_percent}% (-₹{discount_amount})
- Insurance: {insurance_coverage_percent}% (-₹{insurance_coverage_amount})
- Final Amount Payable: ₹{final_amount_payable}
- Doctor: {doctor['fullname']} ({doctor['specialization']})

Please visit the billing counter or use online payment via {payment_method}.

Regards,  
Hospital Admin
"""
    email_sender(patientemailid, email_subject, email_body)

    generatelogs('success', f"Billing created for {patientemailid} by {doctoremailid} with Bill ID {bill_id}", 'billingops/createbill.py')

    return jsonify({
        "status": True,
        "message": "Bill created successfully",
        "bill_id": bill_id,
        "gross_total": gross_total,
        "final_amount": final_amount_payable
    }), 200
