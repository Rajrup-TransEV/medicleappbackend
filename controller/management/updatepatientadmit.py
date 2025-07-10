from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

updatepatientadmitxbp = Blueprint('updatepatientadmitxbp', __name__)

@updatepatientadmitxbp.route('/admitops/updatepadmit', methods=['POST'])
def updateadmitfn():
    admitid = str(request.form.get('admitid'))  # Using uid from your input
    patientstatus = str(request.form.get('patientstatus'))
    print("incoming patient status",patientstatus)
    if not patientstatus:  # Check if patientstatus is provided
        return jsonify({"message": "Patient status is required."}), 400

    try:
        db = get_db_connection()
        admitops = db['patientadmit']
        admitfindbyid = admitops.find_one({"uid":admitid})
        if admitfindbyid:
            result = admitops.update({"uid": admitid}, {"$set": {"patientstatus": patientstatus}})
        return jsonify({"message": "Patient status updated successfully"}), 200
    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'updatepatientadmit.py')
        return jsonify({"error": f"{str(e)}"}), 500
