"""
admin delete account data
"""
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deleteadminaccountbp = Blueprint('deleteadminaccountbp',__name__)

@deleteadminaccountbp.route('/adminops/deleteadminprofile',methods=["POST"])
def deleteadminpf():
    adminid = str(request.form.get('adminid'))
    try:
        db = get_db_connection()
        adminprofile = db['admins']
        findone = adminprofile.find_one({"uid":adminid})
        if findone:
            adminprofile.delete_one({"uid":adminid})
            return jsonify({"message":"account deleted successfully"})
        else:
            generatelogs('info','No admin profile found associated with this id','deleteaccount.py')
            return jsonify({'message':'account not found'}),400
    except Exception as e:
        print(e)
        generatelogs('error',f'{e}','deleteaccount.py')
        return jsonify({'message':'Error deleting account'}),500