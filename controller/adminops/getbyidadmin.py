"""
Get admin by id 
"""
from flask import Blueprint,jsonify,request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs

# MongoDB connection setup
def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'patientops/login.py'
        generatelogs(messagetype, message, filelocation)
        raise

getadminbyidbp = Blueprint('getadminbyidbp',__name__)

@getadminbyidbp.route('/admin/getdetails',methods=['POST'])
def getadminbyidfn():
    adminid = str(request.form.get('adminid'))
    try:
        db = get_db_connection()
        admin_collection = db['admins']
        adminscol = admin_collection.find_one({"uid":adminid})
        if not adminscol:
            return jsonify({"message":"error no admin data found"}),404
        normalpayload = {
            "uid":adminscol.get('uid'),
            "name":adminscol.get('name'),
            "email":adminscol.get('email'),
            "userrole":adminscol.get('userrole')
        }
        return jsonify({"message":"data hasbeen fetched successfully","data":normalpayload}),200
    except Exception as e:
        print(e)
        messagetype = 'error'
        message = f"Error while fetching admin data: {str(e)}"
        filelocation = 'doctorops/getbyidadmin.py'
        generatelogs(messagetype,message,filelocation)
        return jsonify({"error":str(e)}),500