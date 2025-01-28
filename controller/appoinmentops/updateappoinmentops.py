from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

updateappoinmentopsbp = Blueprint('updateappoinmentops', __name__)

@updateappoinmentopsbp.route('/update/appoinment', methods=['POST'])
def updateappnfn():
    appoinid = request.form.get('appoinid')
    appoinmenttime = request.form.get('appoinmenttime')
    appointmentdetails = request.form.get('appointmentdetails')
    appoinmentstatus = request.form.get('appoinmentstatus')

    updatedetails = {}
    
    # Log incoming data for debugging
    generatelogs('info', f"Received update request: {request.form}", 'updateappoinmentops.py')

    # Validate appoinid
    if not appoinid:
        generatelogs('error','Appoinment ID is required','updateappoinmentops.py')
        return jsonify({"message": "Appoinment ID is required"}), 400

    try:
        db = get_db_connection()
        appoinmentops = db['appoinments']
        
        # Prepare fields to update
        if appoinmenttime:
            updatedetails['appoinmenttime'] = appoinmenttime
        if appointmentdetails:
            updatedetails['appoinmentdetails'] = appointmentdetails
        if appoinmentstatus:
            updatedetails['status'] = appoinmentstatus
        
        # Check if there are any fields to update
        if not updatedetails:
            generatelogs('error','No fields to update','updateappoinmentops.py')
            return jsonify({"message": "No fields to update"}), 400
        
        # Perform the update operation using only appoinid
        result = appoinmentops.update_one({"uid": appoinid}, {"$set": updatedetails})
        
        # Check if any documents were modified
        if result.modified_count > 0:
            generatelogs('info', 'Appoinment details have been updated successfully', 'updateappoinmentops.py')
            return jsonify({"message": "Appoinment details have been updated successfully"}), 200
        else:
            generatelogs('warning', 'No matching appointment found or no changes made', 'updateappoinmentops.py')
            return jsonify({"message": "No matching appointment found or no changes made"}), 404
    
    except Exception as e:
        print(e)
        generatelogs('error', f"{str(e)}", 'updateappoinmentops.py')
        return jsonify({"message": "Internal server error"}), 500
