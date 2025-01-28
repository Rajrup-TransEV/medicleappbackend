from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deleteapponbp = Blueprint('deleteapponbp',__name__)

@deleteapponbp.route('/ops/appoinmentdelete',methods=['POST'])
def deleteappnfn():
    appoinid = request.form.get('appoinid')
    try:
        db = get_db_connection()
        appoinmentops = db['appoinments']
        appn = appoinmentops.find_one({"uid":appoinid})
        if appn:
            appoinmentops.delete_one({"uid":appoinid})
            generatelogs('info','Appoinment hasbeen deleted successfully','deleteappn.py')
            return jsonify({'message':'Appoinment hasbeen deleted successfully'})
        else:
            generatelogs("info","No appoinment hasbeen found",'deleteappn.py')
            return jsonify({'message':'No appoinment hasbeen found'})
    except Exception as e:
        print(e)
        generatelogs("error",f'Error deleteting appoinment {str(e)}','deleteappn.py')
        return jsonify({"message":"Internal server error "}),500
