from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

staffupdatebp =  Blueprint('staffupdatebp',__name__)

@staffupdatebp.route('/staffops/updatestaff',methods=['POST'])
def staffupdatefn():
    staffid = str(request.form.get('staffid'))
    staffname = str(request.form.get('staffname'))
    staffdetails = str(request.form.get('staffdetails'))
    hos_gen_staffid = str(request.form.get('hos_gen_staffid'))
    staffage = str(request.form.get('staffage'))
    staffgender = str(request.form.get("staffgender"))
    staffdob =  str(request.form.get("staffdob"))
    stafftype = str(request.form.get('stafftype'))
    staffcategory = str(request.form.get('staffcategory'))
    staffworkingstatus = str(request.form.get('staffworkingstatus'))
    staffsalarytdate = str(request.form.get('staffsalarytdate'))
    staffpaymentstatus = str(request.form.get('staffpaymentstatus'))

 
    updatefields = {}

    if staffname is not None:
        updatefields['staffname']=staffname
    if staffdetails is not None:
        updatefields['staffdetails']=staffdetails
    if hos_gen_staffid is not None:
        updatefields['hos_gen_staffid']=hos_gen_staffid
    if staffage is not None:
        updatefields['staffage'] = staffage
    if staffgender is not None:
        updatefields['staffgender']=staffgender
    if staffdob is not None:
        updatefields['staffdob']=staffdob
    if stafftype is not None:
        updatefields['stafftype']= stafftype
    if staffcategory is not None:
        updatefields['staffcategory'] = staffcategory
    if staffworkingstatus is not None:
        updatefields['staffworkingstatus'] = staffworkingstatus
    if staffsalarytdate is not None:
        updatefields['staffsalarytdate'] = staffsalarytdate
    if staffpaymentstatus is not None:
        updatefields['staffpaymentstatus'] = staffpaymentstatus
    try:
        db = get_db_connection()
        staffcol = db['staffs']
        stafffind = staffcol.find_one({"uid":staffid})
        if stafffind is None:
            return jsonify({'error':"No staff details found with this id"}),404
        result = staffcol.update_one({"uid":staffid},{"$set":updatefields})
        generatelogs('info','Staff details hasbeen successfully updated')
        return jsonify({"message":"staff details hasbeen updated successfully"}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','staffupdate.py')
        return jsonify({"error":f'{str(e)}'}),500