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

faqdeletebp = Blueprint('faqdeletebp',__name__)

@faqdeletebp.route('/ops/faqdelete',methods=["POST"])
def faqdeletefn():
    faqid = str(request.form.get('faqid'))
    try:
        db = get_db_connection()
        faqcol = db['faq']
        faqfind = faqcol.find_one({"uid":faqid})
        if faqfind:
            faqcol.delete_one({"uid":faqid})
            generatelogs('success','faq hasbeen deleted successfully','faqdelete.py')
            return jsonify({"message":"faq data hasbeen deleted successfully"})
        else:
            return jsonify({"message":"no data found associated with the id"})
    except Exception as e:
        print(e)
        generatelogs('error',f"{str(e)}",'faqdelete.py')
        return jsonify({"message":"internal server error"}),500