from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

# MongoDB connection setup
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallappointmentfeesbp = Blueprint('getallappointmentfeesbp', __name__)

@getallappointmentfeesbp.route('/getallappointmentfees', methods=['GET'])
def getallappointmentfeesfn():
    try:
        db = get_db_connection()
        appointmentfees_collections = db['appointmentfees']
        appointmentfees_cursor = appointmentfees_collections.find()

        fees_list = []
        for fee_doc in appointmentfees_cursor:
            fee_doc.pop('_id', None)  # Remove MongoDB internal _id field if not needed
            fees_list.append({
                'uid': fee_doc.get('uid'),
                'doctoremail': fee_doc.get('doctoremail'),
                'appointmentfees': fee_doc.get('appointmentfees')
            })

        return jsonify(fees_list), 200

    except Exception as e:
        print(e)
        generatelogs('error', f'Error occurred: {str(e)}', 'getallappointmentfees.py')
        return jsonify({"error": "An error occurred!"}), 500
