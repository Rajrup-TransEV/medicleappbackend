from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from utils.logs import generatelogs
import os

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getappoinmentdetailsbp = Blueprint('getappoinmentdetailsbp', __name__)

@getappoinmentdetailsbp.route('/getappoinmentdetails', methods=['POST'])
def appointmentfn():
    # Get parameters from the request and handle potential None values
    patientid = request.form.get('patientid')
    doctorid = request.form.get('doctorid')
    appoinid = request.form.get('appoinid')

    query = {key: value for key, value in {
        'doctorid': doctorid,
        'patientid': patientid,
        'appoinid': appoinid
    }.items() if value and value != 'None'}
    if not query:
        generatelogs('error',"At least one of 'doctorid', 'patientid', or 'appoinid' must be provided.",'getappoinmentdetails.py')        
        return jsonify({"error": "At least one of 'doctorid', 'patientid', or 'appoinid' must be provided."}), 400

    try:
        db = get_db_connection()
        appoinmentops = db['appoinments']
        
        # Fetch the latest appointment details based on the constructed query
        getappndetails_cursor = appoinmentops.find(query).sort("created_at", -1).limit(1)

        # Convert cursor to a list and check if there are any results
        getappndetails_list = list(getappndetails_cursor)
        
        # Check if any appointment details were found
        if not getappndetails_list:
            generatelogs('error','No appointment details found associated with the provided IDs.','getappoinmentdetails.py')
            return jsonify({"message": "No appointment details found associated with the provided IDs."}), 404
        
        # Get the first result from the list (which should be the latest due to sorting)
        getappndetails = getappndetails_list[0]

        # Fetch patient and doctor details based on appointment data
        patient_collections = db['patients']
        patient = patient_collections.find_one({"uid": getappndetails.get('patientid')})
        
        doctor_collection = db['doctors']
        doctor = doctor_collection.find_one({"uid": getappndetails.get('doctorid')})

        # Construct the response payload
        normalpayload = {
            "uid": getappndetails.get('uid'),
            'patient_firstname': patient.get('firstname') if patient else None,
            'patient_lastname': patient.get('lastname') if patient else None,
            'doctor_fullname': doctor.get('fullname') if doctor else None,
            'appoinmenttime': getappndetails.get('appoinmenttime'),
            'appoinmentdetails': getappndetails.get('appoinmentdetails'),
            'appoinmentstatus':getappndetails.get('status'),
            'created_at': getappndetails.get('created_at'),
        }

        # Log successful data fetch
        generatelogs('info', 'Data fetched successfully', 'getappoinmentdetails.py')
        
        # Return the fetched appointment details
        return jsonify({"data": normalpayload}), 200
    
    except Exception as e:
        print(e)
        generatelogs('error', f'{e}', 'getappoinmentdetails.py')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
