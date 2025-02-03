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
getprescribebyidbp = Blueprint('getprescribebyidbp', __name__)

@getprescribebyidbp.route("/doctors/getprescribebyid", methods=['POST'])
def getprescribebyidfn():
    prescribeid = str(request.form.get('prescribeid'))
    
    if not prescribeid:
        return jsonify({"error": "Prescription ID is required"}), 400
    
    try:
        db = get_db_connection()
        prescribe_collection = db['prescribe']
        
        # Fetching the prescription by prescription_id
        prescription = prescribe_collection.find_one({"prescription_id": prescribeid})
        
        if prescription is None:
            generatelogs('error','Prescription not found','getprescribebyid.py')
            return jsonify({"error": "Prescription not found"}), 404
        
        # Omit the _id field from the response
        prescription_data = {key: value for key, value in prescription.items() if key != '_id'}
        
        # Fetching and encoding the PDF file if it exists
        file_path = prescription.get('file_path')
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')
            prescription_data['file_data'] = encoded_string  # Add encoded data to the record
        
        generatelogs('success','Prescription data hasbeen fetched successfully','getprescribebyid.py')
        return jsonify(prescription_data), 200
        
    except Exception as e:
        messagetype = 'error'
        message = f"Error retrieving prescription: {str(e)}"
        filelocation = 'prescribe.py'
        generatelogs(messagetype, message, filelocation)
        
        return jsonify({"error": "An error occurred while processing your request"}), 500
