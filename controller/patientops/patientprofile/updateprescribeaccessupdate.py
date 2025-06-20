from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = 'uploads/doctorprofilepicture'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

prescribeaccessupdate_bp = Blueprint('prescribeaccessupdate_bp', __name__)

@prescribeaccessupdate_bp.route("/patientops/prescribeaccessupdate", methods=["POST"])
def prescribeaccessupdatefn():
    patientid = str(request.form.get('patientid'))
    prescribeid = str(request.form.get('prescribeid'))
    if not patientid:
        return jsonify({"error": "patientid is required"}), 400
    update_fields = {
        "guestaccess": request.form.get('guestaccess')
    }
    try:
        db = get_db_connection()
        prescribecol = db['prescribe']
        prescribecol.update_one({"patientid": patientid,"uid": prescribeid}, {"$set": update_fields})
        return jsonify({"message": "Prescribe access updated successfully"}), 200
    except Exception as e:
        generatelogs('error', str(e), 'doctorsops/prescribeaccessupdate.py')
        return jsonify({"error": str(e)}), 500
