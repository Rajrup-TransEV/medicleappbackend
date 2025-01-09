from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from utils.logs import generatelogs
import os

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getappoinmenthistorybp = Blueprint('getappoinmenthistorybp', __name__)

@getappoinmenthistorybp.route('/getappoinmenthistory', methods=['POST'])
def appointmenthisfn():
    # Get parameters from the request and handle potential None values
    patientid = request.form.get('patientid')
    doctorid = request.form.get('doctorid')
    appoinid = request.form.get('appoinid')

    # Initialize the query dictionary
    query = {key: value for key, value in {
        'doctorid': doctorid,
        'patientid': patientid,
        'appoinid': appoinid
    }.items() if value and value != 'None'}

    print(query)  # Debugging output to see what query is being constructed

    # Check if the query is empty, which means no valid parameters were provided
    if not query:
        return jsonify({"error": "At least one of 'doctorid', 'patientid', or 'appoinid' must be provided."}), 400

    try:
        db = get_db_connection()
        appoinmentops = db['appoinments']
        
        # Fetch all appointment details based on the constructed query
        getappndetails_cursor = appoinmentops.find(query).sort("created_at", -1)

        # Convert cursor to a list
        getappndetails_list = list(getappndetails_cursor)
        
        # Check if any appointment details were found
        if not getappndetails_list:
            return jsonify({"message": "No appointment details found associated with the provided IDs."}), 404
        
        # Prepare a list to hold all appointment details with patient and doctor info
        appointments_with_details = []

        # Fetch patient and doctor details for each appointment
        patient_collection = db['patients']
        doctor_collection = db['doctors']

        for getappndetails in getappndetails_list:
            patient = patient_collection.find_one({"uid": getappndetails.get('patientid')})
            doctor = doctor_collection.find_one({"uid": getappndetails.get('doctorid')})

            # Construct the response payload for each appointment
            appointment_payload = {
                "uid": getappndetails.get('uid'),
                'patient_firstname': patient.get('firstname') if patient else None,
                'patient_lastname': patient.get('lastname') if patient else None,
                'doctor_fullname': doctor.get('fullname') if doctor else None,
                'appoinmenttime': getappndetails.get('appoinmenttime'),
                'appoinmentdetails': getappndetails.get('appoinmentdetails'),
                'created_at': getappndetails.get('created_at'),
            }

            appointments_with_details.append(appointment_payload)

        # Log successful data fetch
        generatelogs('info', 'Data fetched successfully', 'getappoinmentdetails.py')
        
        # Return all fetched appointment details
        return jsonify({"data": appointments_with_details}), 200
    
    except Exception as e:
        print(e)
        generatelogs('error', f'{e}', 'getappoinmentdetails.py')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
