from flask import Blueprint,jsonify,request
import os
from pymongo import MongoClient
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deleteleave_bp = Blueprint('deleteleave_bp',__name__)

@deleteleave_bp.route('/doctorsops/deleteleave',methods=['POST'])
def deleteleavefn():
    leaveid = str(request.form.get('leaveid'))
    try:
        db = get_db_connection()
        leavecollection = db['doctorleave']
        leave = leavecollection.find_one({'uid': leaveid})
        if leave:
            leavecollection.delete_one({'uid': leaveid})
            generatelogs("info","Leave deleted successfully","deleteleave.py")
            return jsonify({'message': 'Leave deleted successfully'}),200
        else:
            generatelogs("info","Leave not found","deleteleave.py")
            return jsonify({'message': 'Leave not found'}),404
    except Exception as e:
        print(e)
        generatelogs("error",f"{str(e)}","deleteleave.py")
        return jsonify({'message': 'Error deleting leave'}),500