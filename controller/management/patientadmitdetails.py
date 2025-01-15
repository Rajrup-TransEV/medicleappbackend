from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

patientadmitdetailsbp = Blueprint('patientadmitdetailsbp', __name__)

@patientadmitdetailsbp.route('/ops/patientadmitstatus', methods=['POST'])
def patientadmitstatus():
    patientid = request.form.get("patientid")
    try:
        db = get_db_connection()
        
        # Fetch patient details
        patientdetails = db['patients'].find_one({"uid": patientid})
        if not patientdetails:
            return jsonify({"error": "Patient not found"}), 404
        
        # Extracting patient details safely
        patientemail = patientdetails.get('email')
        patientfirstname = patientdetails.get('firstname')
        patientage = patientdetails.get('age')
        patientgender = patientdetails.get('gender')
        patientphoneno = patientdetails.get('phonenumber')
        
        # Fetch admission details
        admitcol = db['patientadmit'].find_one({"patientid": patientid})
        if not admitcol:
            return jsonify({"error": "No admission record found for this patient"}), 404
        
        # Extracting admission details safely
        admitstatus = admitcol.get('patientstatus')
        wardid = admitcol.get('ward_id')
        
        # Fetch ward details
        ward = db['wards'].find_one({"uid": wardid})
        if not ward:
            return jsonify({"error": "Ward not found"}), 404
        
        wardemail = ward.get("ward_email")
        wardname = ward.get("name")
        
        # Fetch room details
        roomid = admitcol.get('room_id')
        room_details = db['rooms'].find_one({"uid": roomid})
        
        if not room_details:
            return jsonify({"error": "Room not found"}), 404
        
        room_number = room_details.get("room_number")
        room_type = room_details.get("room_type")
        
        # Prepare response payload
        normal_payload = {
            'patientemail': patientemail,
            'patientfirstname': patientfirstname,
            'patientage': patientage,
            'patientgender': patientgender,
            'patientphoneno': patientphoneno,
            'admitstatus': admitstatus,
            'wardemail': wardemail,
            'wardname': wardname,
            'room_number': room_number,
            'room_type': room_type
        }
        
        generatelogs('success', 'Patient details have been fetched', 'patientadmitstats.py')
        
        return jsonify({"message": "Patient details have been fetched", "data": normal_payload}), 200

    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'patientadmit')
        return jsonify({"error": "Internal server error"}), 500
