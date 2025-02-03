from flask import Blueprint, jsonify,request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deletedoctor_bp = Blueprint('deletedoctor_bp',__name__)

@deletedoctor_bp.route('/doctorsops/deletedoctor',methods=['POST'])
def deletedocfn():
    doctorid = str(request.form.get('doctorid'))
    try:
        db = get_db_connection()
        doctorcollection = db['doctors']
        doctor = doctorcollection.find_one({'uid': doctorid})
        if doctor:
            doctorcollection.delete_one({'uid': doctorid})
            generatelogs("info","Doctor profile deleted successfully","deletedoctor.py")
            return jsonify({'message': 'Doctor profile deleted successfully'}),200
        else:
            generatelogs("info","Doctor profile not found","deletedoctor.py")
            return jsonify({'message': 'Doctor profile not found'}),404
    except Exception as e:
        print(e)
        generatelogs("error","Error deleting doctor profile","deletedoctor.py")
        return jsonify({'message': 'Error deleting doctor profile'}),500