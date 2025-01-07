"""
get appoinment details by patientid , doctorid, appoinmentid
"""
from flask import Blueprint,jsonify, request
from pymongo import MongoClient
from utils.logs import generatelogs
import os

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getappoinmentdetailsbp = Blueprint('getappoinmentdetailsbp',__name__)

@getappoinmentdetailsbp.route('/getappoinmentdetails',methods=['POST'])
def appointmentfn():
    patientid = str(request.form.get('patientid'))
    doctorid = str(request.form.get('doctorid'))
    appoinid = str(request.form.get('appoinid'))
    print(patientid)
    try:
        db = get_db_connection()
        appoinmentops = db['appoinments']
        query = {}
        print (query)
        if doctorid:
            query['doctorid']=doctorid
        if patientid:
            query['patientid'] = patientid
        if appoinid:
            query['appoinid'] = appoinid
        getappndetails = appoinmentops.find_one(query)
        print(getappndetails)
        # if not getappndetails:
        #     return jsonify({"message":"No appoinment details found associated to the id"}),404
        generatelogs('info','data fetched successfully','getappoinmentdetails.py')
        return jsonify({"data":getappndetails})
    except Exception as e:
        print(e)
        generatelogs('error',f'{e}','getappoinmentdetails.py')
        return jsonify({"error":f"{e}"})