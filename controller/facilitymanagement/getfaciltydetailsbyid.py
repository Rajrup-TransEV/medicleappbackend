from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getfacilitydetailsbyidbp = Blueprint('getfacilitydetailsbyidbp',__name__)

@getfacilitydetailsbyidbp.route('/facilityops/getfacilitydetailsbyid',methods=['POST'])
def facilityfn():
    facilityid = str(request.form.get('facilityid'))
    try:
        db = get_db_connection()
        faicliitycol = db['departments']
        facilitydata = faicliitycol.find({"uid":facilityid})
        results = []
        for faciltiy in facilitydata:
            normalpayload = {
                'departmentid':faciltiy.get('uid'),
                'hospital_assignedid':faciltiy.get('department_hos_id'),
                'Department_Name':faciltiy.get('department_name'),
                'Department_details':faciltiy.get('department_details'),
                'Department_head_name':faciltiy.get('department_head_name'),
                'Department_email':faciltiy.get('department_officialemail'),
                'Department_phoneno':faciltiy.get('department_official_phoneno'),
                'Created At':faciltiy.get('created_at'),
                'Department status':faciltiy.get('departmentstatus'),
                'Department Opentime':faciltiy.get('department_opentime'),
                'Department Closetime':faciltiy.get('department_closetime')
            }
            results.append(normalpayload)
        generatelogs('success',"All of the department data hasbeen fetched successfully",'getfacilitydetailsbyid.py')
        return jsonify({'message':'All of data hasbeen fetched','payload':results}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getfacilitydetailsbyid.py')
        return jsonify({'error':'Internal server error occurred'}),500