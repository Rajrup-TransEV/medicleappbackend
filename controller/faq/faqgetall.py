from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

faqgetallbp = Blueprint('faqgetallbp',__name__)

@faqgetallbp.route('/faq/getall',methods=['POST'])
def faqgetallfn():
    try:
        db = get_db_connection()
        faqcol = db['faq']
        allfaq = faqcol.find()
        results = []
        for i in allfaq:
            payloaddata = {
                'uid':i.get('uid'),
                'faqquestion':i.get('faqquestion'),
                'faqdescription':i.get('faqdescription'),
                'created_at':i.get('created_at')
            }
            results.append(payloaddata)
        generatelogs('success','faq all get','faqgetall.py')
        return jsonify({'message':'all department data hasbeen fetched','data':results})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','faqgetall.py')
        return jsonify({'error':f'{str(e)}'}),500