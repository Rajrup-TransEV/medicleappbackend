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

labdataaccessupdate_bp = Blueprint('labdataaccessupdate_bp', __name__)

@labdataaccessupdate_bp.route("/patientops/labdataaccessupdate", methods=["POST"])
def labdataaccessupdatefn():
    patientid = str(request.form.get('patientid'))
    labid = str(request.form.get('labid'))
    if not patientid:
        return jsonify({"error": "patientid is required"}), 400
    update_fields = {
        "guestaccess": request.form.get('guestaccess')
    }
    try:
        db = get_db_connection()
        labcol = db['labreports']
        labcol.update_one({"patientid": patientid,"uid": labid}, {"$set": update_fields})
        return jsonify({"message": "Lab data access updated successfully"}), 200
    except Exception as e:
        generatelogs('error', str(e), 'doctorsops/labdataaccessupdate.py')
        return jsonify({"error": str(e)}), 500
