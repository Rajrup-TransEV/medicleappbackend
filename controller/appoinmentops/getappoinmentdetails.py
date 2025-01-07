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

    # Initialize the query dictionary
    query = {}
    
    # Populate the query based on provided parameters
    if doctorid and doctorid != 'None':
        query['doctorid'] = doctorid
    if patientid and patientid != 'None':
        query['patientid'] = patientid
    if appoinid and appoinid != 'None':
        query['appoinid'] = appoinid

    print(query)  # Debugging output to see what query is being constructed

    # Check if the query is empty, which means no valid parameters were provided
    if not query:
        return jsonify({"error": "At least one of 'doctorid', 'patientid', or 'appoinid' must be provided."}), 400

    try:
        db = get_db_connection()
        appoinmentops = db['appoinments']
        
        # Fetch appointment details based on the constructed query
        getappndetails = appoinmentops.find_one(query)
        patient_collections = db['patients']
        patient = patient_collections.find_one({"uid":getappndetails.get('patientid')})
        doctor_collection = db['doctors']
        doctor = doctor_collection.find_one({"uid": getappndetails.get('doctorid')})
        # Check if any appointment details were found
        if not getappndetails:
            return jsonify({"message": "No appointment details found associated with the provided IDs."}), 404
        
        normalpayload = {
            "uid":getappndetails.get('uid'),
            'patient_firstname':patient['firstname'] if patient else None,
            'patient_lastname':patient['lastname'] if patient else None,
            'doctor_fullname': doctor['fullname'] if doctor else None,
              'appoinmenttime':getappndetails.get('appoinmenttime'),
                'appoinmentdetails':getappndetails.get('appoinmentdetails'),
            'created_at':getappndetails.get('created_at'),
        }
        # Log successful data fetch
        generatelogs('info', 'Data fetched successfully', 'getappoinmentdetails.py')
        
        # Return the fetched appointment details
        return jsonify({"data": normalpayload}), 200
    
    except Exception as e:
        print(e)
        generatelogs('error', f'{e}', 'getappoinmentdetails.py')
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
