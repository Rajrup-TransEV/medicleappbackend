from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import pytz
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

# DB connection
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

update_billbp = Blueprint('update_billbp', __name__)

@update_billbp.route('/billing/updatebill', methods=['POST'])
def updatebillfn():
    db = get_db_connection()
    billing_collection = db['billing']

    try:
        bill_id = str(request.form.get('billid'))
        if not bill_id:
            return jsonify({"status": False, "message": "Bill ID is required"}), 400

        bill = billing_collection.find_one({"bill_id": bill_id})
        if not bill:
            return jsonify({"status": False, "message": "Bill not found"}), 404

        # Prepare updated fields
        update_fields = {}

        # Optional fields to update
        optional_fields = [
            "purpose", "room_type", "treatment_type", "treatment_duration_days",
            "medicine_charge", "lab_charge", "other_charges", "discount_percent",
            "insurance_provider", "insurance_coverage_percent", "payment_method",
            "payment_status", "notes"
        ]

        for field in optional_fields:
            value = request.form.get(field)
            if value is not None:
                if field in ["medicine_charge", "lab_charge", "other_charges", "discount_percent", "insurance_coverage_percent"]:
                    value = float(value)
                elif field == "treatment_duration_days":
                    value = int(value)
                update_fields[field] = value

        # Recalculate charges if necessary
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

        # Use updated or existing values
        room_type = update_fields.get("room_type", bill.get("room_type", "general")).lower()
        treatment_type = update_fields.get("treatment_type", bill.get("treatment_type", "consultation")).lower()
        treatment_duration = update_fields.get("treatment_duration_days", bill.get("treatment_duration_days", 1))

        room_charge = room_cost.get(room_type, 1000) * treatment_duration
        treatment_charge = treatment_costs.get(treatment_type, 1000)

        medicine_charge = update_fields.get("medicine_charge", bill.get("medicine_charge", 0))
        lab_charge = update_fields.get("lab_charge", bill.get("lab_charge", 0))
        other_charges = update_fields.get("other_charges", bill.get("other_charges", 0))

        gross_total = room_charge + treatment_charge + medicine_charge + lab_charge + other_charges

        discount_percent = update_fields.get("discount_percent", bill.get("discount_percent", 0))
        discount_amount = (discount_percent / 100) * gross_total

        after_discount = gross_total - discount_amount

        insurance_coverage_percent = update_fields.get("insurance_coverage_percent", bill.get("insurance_coverage_percent", 0))
        insurance_coverage_amount = (insurance_coverage_percent / 100) * after_discount

        final_amount_payable = after_discount - insurance_coverage_amount

        update_fields.update({
            "room_charge": room_charge,
            "treatment_charge": treatment_charge,
            "gross_total": gross_total,
            "discount_amount": discount_amount,
            "insurance_coverage_amount": insurance_coverage_amount,
            "final_amount_payable": final_amount_payable,
            "final_amount": final_amount_payable,  # <--- Added here
            "updated_at": now.isoformat()
        })

        # Perform update
        billing_collection.update_one({"bill_id": bill_id}, {"$set": update_fields})

        generatelogs("success", f"Bill with ID {bill_id} updated successfully", "updatebill.py")
        return jsonify({"status": True, "message": "Bill updated successfully", "bill_id": bill_id}), 200

    except Exception as e:
        generatelogs("error", f"Error while updating bill: {str(e)}", "updatebill.py")
        return jsonify({"status": False, "message": str(e)}), 500
