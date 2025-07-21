from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labdeletebp = Blueprint('labdeletebp',__name__)

@labdeletebp.route('/ops/deletelabs',methods=['POST'])
def labdeletefn():
    labreportid = str(request.form.get('labreportid'))
    try:
        db = get_db_connection()
        reportcol = db['labreports']
        findonereport = reportcol.find_one({"uid":labreportid})
        if findonereport:
            reportcol.delete_one({"uid":labreportid})
            return jsonify({"message":"Data deleted successfully"})
        else:
            return jsonify({"error":"no report get"})
    except Exception as e:
        print(str(e))
        return jsonify({"e":f'{str(e)}'})