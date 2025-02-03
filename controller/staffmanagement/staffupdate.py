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

staffupdatebp = Blueprint('staffupdatebp', __name__)

@staffupdatebp.route('/staffops/updatestaff', methods=['POST'])
def staffupdatefn():
    staffid = str(request.form.get('staffid'))
    
    # Collecting fields from the request
    staffname = request.form.get('staffname')
    staffdetails = request.form.get('staffdetails')
    hos_gen_staffid = request.form.get('hos_gen_staffid')
    staffage = request.form.get('staffage')
    staffgender = request.form.get("staffgender")
    staffdob = request.form.get("staffdob")
    stafftype = request.form.get('stafftype')
    staffcategory = request.form.get('staffcategory')
    staffworkingstatus = request.form.get('staffworkingstatus')
    staffsalarytdate = request.form.get('staffsalarytdate')
    staffpaymentstatus = request.form.get('staffpaymentstatus')

    updatefields = {}

    # Only add fields that are not None or empty
    if staffname:
        updatefields['staffname'] = staffname
    if staffdetails:
        updatefields['staffdetails'] = staffdetails
    if hos_gen_staffid:
        updatefields['hos_gen_staffid'] = hos_gen_staffid
    if staffage:
        updatefields['staffage'] = staffage
    if staffgender:
        updatefields['staffgender'] = staffgender
    if staffdob:
        updatefields['staffdob'] = staffdob
    if stafftype:
        updatefields['stafftype'] = stafftype
    if staffcategory:
        updatefields['staffcategory'] = staffcategory
    if staffworkingstatus:
        updatefields['staffworkingstatus'] = staffworkingstatus
    if staffsalarytdate:
        updatefields['staffsalarytdate'] = staffsalarytdate
    if staffpaymentstatus:
        updatefields['staffpaymentstatus'] = staffpaymentstatus

    try:
        db = get_db_connection()
        staffcol = db['staffs']
        
      
        stafffind = staffcol.find_one({"uid": staffid})
        if not stafffind:
            return jsonify({'error': "No staff details found with this id"}), 404
        
    
        result = staffcol.update_one({"uid": staffid}, {"$set": updatefields})

        generatelogs('info', 'Staff details have been successfully updated', 'staffupdate.py')
        return jsonify({"message": "Staff details have been updated successfully"}), 200

    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'staffupdate.py')
        return jsonify({"error": f'{str(e)}'}), 500
