"""
get all appoinment details
"""
from flask import Blueprint,jsonify,request
from pymongo import MongoClient
from utils.logs import generatelogs
import os


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallappoinmentbp = Blueprint('getallappoinmentbp',__name__)

@getallappoinmentbp.route('/getallappoinment',methods=['GET'])
def getallappnfn():
    try:
        db = get_db_connection()
        allappoinmentcollections = db['appoinments']
        doctor_collection = db['doctors']
        patient_collections = db['patients']
        appoinmentfinds = allappoinmentcollections.find()
        appoinmentlist = []
        
     
        for appoinment in appoinmentfinds:
            doctor = doctor_collection.find_one({"uid": appoinment.get('doctorid')})
            patient = patient_collections.find_one({"uid":appoinment.get('patientid')})
            appoinment_data = {
                'uid':appoinment.get('uid'),
                'doctor_fullname': doctor['fullname'] if doctor else None,
                'doctorid':appoinment.get('doctorid'),
                'appoinmenttime':appoinment.get('appoinmenttime'),
                'appoinmentdetails':appoinment.get('appoinmentdetails'),
                'appoinmentstatus':appoinment.get('status'),
                'patientid':appoinment.get('patientid'),
                'patient_firstname':patient['firstname'] if patient else None,
                'patient_lastname':patient['lastname'] if patient else None,
                'created_at':appoinment.get('created_at'),
            }
            appoinmentlist.append(appoinment_data)
        generatelogs("success",'Appoinment data hasbeen fetched successfully','getallappoinmentdetails.py')
        return jsonify({"message":"Appoinment data hasbeen fetched successfully","data":appoinmentlist})
    except Exception as e:
        generatelogs("error",f"{str(e)}","getallappoinmentdetails.py")
        return jsonify({"message":"Error fetching leave data Internal server error"}),500