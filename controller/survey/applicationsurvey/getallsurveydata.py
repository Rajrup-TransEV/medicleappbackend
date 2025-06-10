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

getallsurveybp = Blueprint('getallsurveybp',__name__)

@getallsurveybp.route('/ops/getallsurvey',methods=['GET'])
def getallsurveyfn():
    try:
        db = get_db_connection()
        surveycol = db['survey']
        surveys = surveycol.find()
        result = []
        for survey in surveys:
            normalpayload = {
                'uid':survey.get('uid'),
                'name':survey.get('email'),
                'ratingnumber':survey.get('ratingnumber'),
                'feedbackmessage':survey.get('feedbackmessage'),
                'associatedadminid':survey.get('associatedadminid'),
                'feedbacktype':survey.get('feedbacktype')
            }
            result.append(normalpayload)
        generatelogs('success','survey data fetched successfully','getallsurveydata.py')
        return jsonify({"message":"management","data":result}),200
    except Exception as e:
        print(e)
        generatelogs('error',"survey data fetch failed","getallsurveydata.py")
        return jsonify({'error':f'{str(e)}'}),500