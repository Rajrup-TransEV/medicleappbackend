from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labupdatebp = Blueprint('labupdatebp',__name__)

@labupdatebp.route('/ops/labupdate',methods=['POST'])
def labupdatefn():
    labid = str(request.form.get('labid'))
    patientid = str(request.form.get('patientid'))
    labphyreportid = str(request.form.get('labphyreportid'))
    patientsymptoms = str(request.form.get('patientsymptoms'))
    doctorreferal = str(request.form.get('doctorreferal'))
    typeoftest = str(request.form.get('typeoftest'))
    finalreport = str(request.form.get('finalreport'))

    updatefields = {}
    if patientid is not None:
        updatefields['patientid'] = patientid
    if labphyreportid is not None:
        updatefields['labphyreportid'] = labphyreportid
    if patientsymptoms is not None:
        updatefields['patientsymptoms'] = patientsymptoms
    if doctorreferal is not None:
        updatefields['doctorreferal'] = doctorreferal
    if typeoftest is not None:
        updatefields['typeoftest'] = typeoftest
    if finalreport is not None:
        updatefields['finalreport'] = finalreport
    try:
        db = get_db_connection()
        labcol = db['labreports'].update_one({"uid":labid},{"$set":updatefields})
        # generatelogs('info','')
    except Exception as e:
        print(e)
        generatelogs('error')