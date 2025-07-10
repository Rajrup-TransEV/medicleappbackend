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

emservicebyidbp = Blueprint('emservicebyidbp', __name__)

@emservicebyidbp.route('/ops/emservicebyid', methods=['POST'])
def emservicebyidfn():
    emserviceid = str(request.form.get('emserviceid'))
    try:
        db = get_db_connection()
        emservicecol = db['emservice']
        emservicefind = emservicecol.find_one({"uid": emserviceid})
        if emservicefind:
            emservicefind.pop('_id', None)  # Remove _id from the response
            generatelogs('success', 'emservice data by id hasbeen fetched', 'emservicebyid.py')
            return jsonify({"message": "emservice data by id hasbeen fetched", "data": emservicefind}), 200
        else:
            generatelogs("info", "No emservice hasbeen found", 'emservicebyid.py')
            return jsonify({'message': 'No emservice hasbeen found'})
    except Exception as e:
        print(e)
        generatelogs('error', f"{str(e)}", 'emservicebyid.py')
        return jsonify({"error": f'{str(e)}'}), 500
