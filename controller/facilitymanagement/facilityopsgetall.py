from flask import Blueprint, jsonify
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

facilityopsgetallbp  = Blueprint('facilityopsgetallbp',__name__)

@facilityopsgetallbp.route('/facilityops/getallfacility')
def facilityfn():
    try:
        db  = get_db_connection()
        departmentcol = db['departments']
        departments = departmentcol.find()
        results = []
        for department in departments:
            department_data = {
                'uid':department.get('uid'),
                'department_name':department.get('department_name'),
                'department_details':department.get('department_details'),
                'department_hos_id':department.get('department_hos_id'),
                'department_head_name':department.get('department_head_name'),
                'department_officialemail':department.get('department_officialemail'),
                'department_official_phoneno':department.get('department_official_phoneno'),
                'created_at':department.get('created_at'),
                'departmentstatus':department.get('departmentstatus'),
                'department_opentime':department.get('department_opentime'),
                'department_closetime':department.get('department_closetime')
            }
            results.append(department_data)
        generatelogs('success','all department data hasbeen fetched successfully','facilityopsgetall.py')
        return jsonify({"message":'all department data hasbeen fetched successfully','data':results}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','facilityopsgetall.py')
        return jsonify({'error':f'{str(e)}'}),500