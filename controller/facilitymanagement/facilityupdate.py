from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

facilityupdatebp = Blueprint('facilityupdatebp',__name__)

@facilityupdatebp.route("/facilityops/updatefacilitydata",methods=['POST'])
def facilityupdatefn():
    facilityid = str(request.form.get('facilityid'))
    departmentname = str(request.form.get('departmentname'))
    department_details= str(request.form.get('department_details'))
    department_hos_id = str(request.form.get('department_hos_id'))
    department_head_name =  str(request.form.get('department_head_name'))
    department_officialemail =  str(request.form.get('department_officialemail'))
    department_official_phoneno = str(request.form.get('department_official_phoneno'))
    departmentstatus = str(request.form.get('departmentstatus'))
    department_opentime = str(request.form.get('department_opentime'))
    department_closetime = str(request.form.get('department_closetime'))

    updatefields = {}
    if departmentname is not None:
        updatefields['department_name'] = departmentname
    if department_details is not None:
        updatefields['department_details'] = department_details
    if department_hos_id  is not None:
        updatefields['department_hos_id'] = department_hos_id
    if department_head_name is not None:
        updatefields['department_hos_id'] = department_hos_id
    if department_officialemail is not None:
        updatefields['department_officialemail']=department_officialemail
    if department_official_phoneno is not None:
        updatefields['department_official_phoneno']=department_official_phoneno
    if departmentstatus is not None:
        updatefields['departmentstatus']=departmentstatus
    if department_opentime is not None:
        updatefields['department_opentime']=department_opentime
    if department_closetime is not None:
        updatefields['department_closetime']=department_closetime
    try:
        db  = get_db_connection()
        facilityops = db['departments']
        result = facilityops.update_one({'uid':facilityid},{"$set":updatefields})
        generatelogs('info','Facility details hasbeen successfully updated','facilityupdate.py')
        return jsonify({"message":"Facility details hasbeen successfully updated",'data':updatefields})    
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','facilityupdate.py')
        return jsonify({"message":f"{str(e)}"})