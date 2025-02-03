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

deletestaffxbp = Blueprint('deletestaffxbp',__name__)

@deletestaffxbp.route('/ops/staffdelete', methods=['POST'])
def deletestafffn():
    staffid = str(request.form.get('staffid'))
    try:
        db = get_db_connection()
        staffcol  = db['staffs']
        stafffind = staffcol.find_one({"uid":staffid})
        if stafffind:
            staffcol.delete_one({"uid":staffid})
            generatelogs('info',"staff hasbeen successfully deleted from database",'staffdelete.py')
            return jsonify({"message":"staff hasbeen successfully deleted from database"}),200

    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','staffdelete.py')
        return jsonify({'message':f'{str(e)}'}),500