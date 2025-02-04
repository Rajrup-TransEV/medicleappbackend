from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

medicalsurveycreatebp = Blueprint('medicalsurveycreatebp',__name__)

@medicalsurveycreatebp.route('/ops/createmsurvey',methods=['POST'])
def medicalsurveyfn():
    required_fields = [
        'surveyor_name', 
        "surveyor_contact", 
        'housenumber', 
        'wardnumber',
        'membercount', 
        'gurdian_of_the_house',
        'number_of_sick_persons',
        'name_of_the_sick_persons'
        'reason_of_sickness',
        'medical_remedy',
        'district', 
        "localaddress", 
        "ps_name", 
        "pincode"
    ]

    form_data = {field: request.form.get(field) for field in required_fields}
   
    surveyor_name = str(form_data['surveyor_name'])
    surveyor_contact = str(form_data['surveyor_contact'])
    housenumber = str(form_data['housenumber'])
    wardnumber = str(form_data['wardnumber'])
    membercount = str(form_data['membercount'])
    gurdian_of_the_house = str(form_data['gurdian_of_the_house'])
    number_of_sick_persons = str(form_data['number_of_sick_persons'])
    name_of_the_sick_persons = str(form_data['name_of_the_sick_persons'])
    reason_of_sickness = str(form_data['reason_of_sickness'])
    medical_remedy = str(form_data['medical_remedy'])
    district = str(form_data['district'])
    localaddress = str(form_data['localaddress'])
    ps_name = str(form_data['ps_name'])
    pincode = str(form_data['pincode'])

    try:
        db = get_db_connection()
        mscol = db['medicalsurvey']
        uuidx = str(uuid.uuid4())
        mscol.insert_one({
            'uid':uuidx,
            'surveyor_name':surveyor_name,
            'surveyor_contact':surveyor_contact,
            'housenumber':housenumber,
            'wardnumber':wardnumber,
            'membercount':membercount,
            'gurdian_of_the_house':gurdian_of_the_house,
            'number_of_sick_persons':number_of_sick_persons,
            'name_of_the_sick_persons':name_of_the_sick_persons,
            'reason_of_sickness':reason_of_sickness,
            'medical_remedy':medical_remedy,
            'district':district,
            'localaddress':localaddress,
            'ps_name':ps_name,
            'pincode':pincode
        })
        generatelogs('success','medical survey hasbeen created','medicalsurverycreate.py')
        return jsonify({'message':'medical survey hasbeen saved','surveyid':uuidx})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','medicalsurverycreate.py')
        return jsonify({'error',f'{str(e)}'}),500