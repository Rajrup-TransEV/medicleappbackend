from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
import base64
from dotenv import load_dotenv


load_dotenv()

UPLOAD_FOLDER = 'uploads/medicaldirectory/prescribe/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db

getprescribebypatientidbp = Blueprint('getprescribebypatientidbp', __name__)

@getprescribebypatientidbp.route("/doctors/getprescribebypatientid", methods=['POST'])
def getprescribebyidfn():
    patientid = str(request.form.get('patientid'))
    
    if not patientid:
        generatelogs('error','Patient ID is required','getprescrbbypatientid.py')
        return jsonify({"error": "Patient ID is required"}), 400
    
    try:
        db = get_db_connection()
        prescribe_collection = db['prescribe']
        
        # Fetching all prescriptions for the given patient ID
        prescriptions = prescribe_collection.find({"patientid": patientid})
        
        results = []
        
        for prescription in prescriptions:
            # Omit the _id field from the response
            prescription_data = {key: value for key, value in prescription.items() if key != '_id'}
            
            # Fetching and encoding the PDF file if it exists
            file_path = prescription.get('file_path')
            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as pdf_file:
                    encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')
                prescription_data['file_data'] = encoded_string  # Add encoded data to the record
            
            results.append(prescription_data)
        
        if not results:
            generatelogs('error','No prescriptions found for this patient','getprescrbbypatientid.py')
            return jsonify({"error": "No prescriptions found for this patient"}), 404
        generatelogs("success",'prescriptions hasbeen found','getprescrbbypatientid.py')
        return jsonify(results), 200
        
    except Exception as e:
        messagetype = 'error'
        message = f"Error retrieving prescriptions: {str(e)}"
        filelocation = 'prescribe.py'
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": "An error occurred while processing your request"}), 500
