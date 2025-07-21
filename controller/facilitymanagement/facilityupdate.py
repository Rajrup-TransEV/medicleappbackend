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

facilityupdatebp = Blueprint('facilityupdatebp',__name__)


@facilityupdatebp.route("/facilityops/updatefacilitydata", methods=['POST'])
def facilityupdatefn():
    try:
        # Try to get JSON data
        data = request.form

        facilityid = data.get('facilityid')
        departmentname = data.get('departmentname')
        department_details = data.get('department_details')
        department_hos_id = data.get('department_hos_id')
        department_head_name = data.get('department_head_name')
        department_officialemail = data.get('department_officialemail')
        department_official_phoneno = data.get('department_official_phoneno')
        departmentstatus = data.get('departmentstatus')
        department_opentime = data.get('department_opentime')
        department_closetime = data.get('department_closetime')

        if not facilityid:
            return jsonify({"message": "facilityid is required"}), 400

        updatefields = {}
        if departmentname is not None:
            updatefields['department_name'] = departmentname
        if department_details is not None:
            updatefields['department_details'] = department_details
        if department_hos_id is not None:
            updatefields['department_hos_id'] = department_hos_id
        if department_head_name is not None:
            updatefields['department_head_name'] = department_head_name
        if department_officialemail is not None:
            updatefields['department_officialemail'] = department_officialemail
        if department_official_phoneno is not None:
            updatefields['department_official_phoneno'] = department_official_phoneno
        if departmentstatus is not None:
            updatefields['departmentstatus'] = departmentstatus
        if department_opentime is not None:
            updatefields['department_opentime'] = department_opentime
        if department_closetime is not None:
            updatefields['department_closetime'] = department_closetime

        if not updatefields:
            return jsonify({"message": "No fields to update"}), 400

        db = get_db_connection()
        facilityops = db['departments']
        result = facilityops.update_one({'uid': facilityid}, {"$set": updatefields})

        if result.matched_count == 0:
            return jsonify({"message": "Facility not found"}), 404

        generatelogs('info', 'Facility details have been successfully updated', 'facilityupdate.py')
        return jsonify({"message": "Facility details have been successfully updated", 'data': updatefields})

    except Exception as e:
        print(e)
        generatelogs('error', str(e), 'facilityupdate.py')
        return jsonify({"message": str(e)}), 500


