from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from datetime import datetime
from utils.logs import generatelogs
from lib.emailsender import email_sender

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

assignbedtopatientbp = Blueprint("assignbedtopatientbp", __name__)

@assignbedtopatientbp.route("/ops/patientadmit", methods=['POST'])
def assignbedtopatientfn():
    # Get the current timezone
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)
    
    ward_id = request.form.get('ward_id')
    room_id = request.form.get('room_id')
    patientid = request.form.get("patientid")

    try:
        db = get_db_connection()
        
        # Check if the patient is already admitted
        existing_admission = db['patientadmit'].find_one({"patientid": patientid})
        
        if existing_admission:
            if existing_admission['patientstatus'] == "admit":
                return jsonify({"error": "Patient is already assigned to a bed"}), 400
            
            elif existing_admission['patientstatus'] == "discharged":
      
                # Update the status of the previous admission to 'readmitted'
                db['patientadmit'].update_one(
                    {"patientid": patientid},
                    {"$set": {"patientstatus": "readmitted", "assigned_at": current_time}}
                )
                          # Optionally log the case of readmission
                generatelogs("info", f"Patient {patientid} is being readmitted after discharge.", "assignedtopatient.py")
                return generatelogs({"success":"patient hasbeen readmitted after discharge"}),201

        
        # Check the room's current capacity
        room = db['rooms'].find_one({"uid": room_id})
        if not room:
            return jsonify({"error": "Room not found"}), 404
        
        if room['capacity'] <= 0:
            return jsonify({"error": "No beds available for assignment"}), 400
        
        # Deduct capacity by 1
        new_capacity = room['capacity'] - 1
        db['rooms'].update_one({"uid": room_id}, {"$set": {"capacity": new_capacity}})
        
        # Assign bed to patient in the 'patientadmit' collection
        uuidx = str(uuid.uuid4())
        admission_record = {
            "patientid": patientid,
            "ward_id": ward_id,
            "room_id": room_id,
            "assigned_at": current_time,
            'patientstatus': "admit",
            "uid": uuidx
        }
        
        db['patientadmit'].insert_one(admission_record)
        
        ward = db['wards'].find_one({"uid": ward_id})
        wardemail = ward.get("ward_email")
        wardname = ward.get("name")
        
        room_details = db['rooms'].find_one({"uid": room_id})
        room_number = room_details.get("room_number")
        room_type = room_details.get("room_type")
        
        patientdetails = db['patients'].find_one({"uid": patientid})
        patientemail = patientdetails.get('email')
        patientfirstname = patientdetails.get('firstname')
        patientage= patientdetails.get('age')
        patientgender = patientdetails.get('gender')
        patientphoneno = patientdetails.get('phonenumber')

        # Email send to ward master
        wardsubject = "Patient has been admitted"
        wardtext = f"""Patient name - {patientfirstname}, 
                        Patient age - {patientage}, 
                        Patient email - {patientemail}, 
                        Patient gender - {patientgender}, 
                        Patient phone number - {patientphoneno} 
                        has been admitted in ward - {wardname} 
                        at room - {room_type} and room number - {room_number}."""
        
        email_sender(wardemail, wardsubject, wardtext)
        
        # Email send to patient
        patientsubject = "Patient has been admitted"
        patienttext = f"""Patient name - {patientfirstname}, 
                          Patient age - {patientage}, 
                          Patient email - {patientemail}, 
                          Patient gender - {patientgender}, 
                          Patient phone number - {patientphoneno} 
                          has been admitted in ward - {wardname} 
                          at room - {room_type} and room number - {room_number}."""
        
        email_sender(patientemail, patientsubject, patienttext)

        generatelogs("success", "Patient has been assigned successfully", "assignedtopatient.py")
        
        return jsonify({"message": "Bed assigned successfully", "new_capacity": new_capacity, "admissionid": uuidx, "createdat": current_time}), 200

    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'assignbedtopatient.py')
        return jsonify({"error": "Internal server error"}), 500
