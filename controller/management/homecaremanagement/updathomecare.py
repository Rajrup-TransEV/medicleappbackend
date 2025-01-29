from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

updatehomecarebp = Blueprint('updatehomecarebp',__name__)

@updatehomecarebp.route('/ops/updatehomecare',methods=['POST'])
def updatehomecarefn():
    homeuid = str(request.form.get('homeuid'))
    assignedstaffid = str(request.form.get('assignedstaffid'))
    patientname = str(request.form.get('patientname'))
    patientdetails = str(request.form.get('patientdetails'))
    patientphonenum = str(request.form.get('patientphonenum'))
    patinetaddress = str(request.form.get('patinetaddress'))
    patientientguardian = str(request.form.get('patientientguardian'))
    patientientguardianphno = str(request.form.get('patientientguardianphno'))
    refrencedoctorname = str(request.form.get('refrencedoctorname'))
    patientid = str(request.form.get('patientid'))
    timefrom = str(request.form.get('timefrom'))
    timeto = str(request.form.get('timeto'))

    try:
        db = get_db_connection()
        homecare = db['homecare']
        update_details = {}
        if assignedstaffid:
            update_details['assignedstaffid'] = assignedstaffid
        if patientname:
            update_details['patientname'] = patientname
        if patientdetails:
            update_details['patientdetails'] = patientdetails
        if patientphonenum:
            update_details['patientphonenum'] = patientphonenum
        if patinetaddress:
            update_details['patinetaddress'] = patinetaddress
        if patientientguardian:
            update_details['patientientguardian'] = patientientguardian
        if patientientguardianphno:
            update_details['patientientguardianphno'] = patientientguardianphno
        if refrencedoctorname:
            update_details['refrencedoctorname'] = refrencedoctorname
        if patientid:
            update_details['patientid'] = patientid
        if timefrom:
            update_details['timefrom'] = timefrom
        if timeto:
            update_details['timeto'] = timeto

        result = homecare.update_one({'uid':homeuid},{"$set":update_details})
        return jsonify({"data":update_details,"message":"data update success"})
    except Exception as e:
        print(e)
        return jsonify({'error':f'{str(e)}'})