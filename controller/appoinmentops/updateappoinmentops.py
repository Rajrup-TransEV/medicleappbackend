from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs


def get_db_connection():
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db

updateappoinmentopsbp = Blueprint('updateappoinmentops',__name__)

@updateappoinmentopsbp.route('/update/appoinment',methods=['POST'])
def updateappnfn():
    patientid = request.form.get('patientid')
    doctorid = request.form.get('doctorid')
    appoinid = request.form.get('appoinid')
    appoinmenttime = str(request.form.get('appoinmenttime'))
    appointmentdetails = str(request.form.get('appointmentdetails'))
    appoinmentstatus = str(request.form.get('appoinmentstatus'))
    updatedetails = {}
    query = {}
    if doctorid and doctorid != 'None':
        query['doctorid'] = doctorid
    if patientid and patientid != 'None':
        query['patientid'] = patientid
    if appoinid and appoinid != 'None':
        query['appoinid'] = appoinid
    try:
        db = get_db_connection()
        appoinmentops = db['appoinments']
        if appoinmenttime is not None:
             updatedetails['appoinmenttime']=appoinmenttime
        if appointmentdetails is not None:
             updatedetails['appoinmentdetails'] = appointmentdetails
        if appoinmentstatus is not None:
             updatedetails['status']=appoinmentstatus
        appoinmentops.update_one(query,{"$set",updatedetails})
        generatelogs('info','Appoinment details hasbeen updated successfully','updateappoinmentops.py')
        return jsonify({"message":"Appoinment details hasbeen updated successfully"}),200
    except Exception as e:
          print(e)
          generatelogs('error',f"{str(e)}",'updateappoinmentops.py')
          return jsonify({"message":"Internal server error"}),500