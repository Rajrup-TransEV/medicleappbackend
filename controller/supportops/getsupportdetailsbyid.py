from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
import base64
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getsupportdetailsbyidbp = Blueprint('getsupportdetailsbyidbp', __name__)

@getsupportdetailsbyidbp.route('/ops/getsupportdetails', methods=['POST'])
def getsupportbyidfn():
    supportid = str(request.form.get('supportid'))
    try:
        db = get_db_connection()
        supportcol = db['support'].find_one({"uid": supportid})
        if supportcol:
            base64_docs = []
            documents = supportcol.get('documents', [])
            for doc_path in documents:
                if os.path.exists(doc_path):
                    with open(doc_path, "rb") as file:
                        encoded = base64.b64encode(file.read()).decode('utf-8')
                        base64_docs.append({
                            "filename": os.path.basename(doc_path),
                            "base64": encoded
                        })
                else:
                    base64_docs.append({
                        "filename": os.path.basename(doc_path),
                        "base64": None,
                        "error": "File not found"
                    })

            normalpayload = {
                "name": supportcol['name'],
                "email": supportcol['email'],
                "phone": supportcol['phone'],
                "issuetype": supportcol['issuetype'],
                "message": supportcol['message'],
                "documents": base64_docs
            }

            generatelogs('success', 'get support details by id', 'getsupportdetails.py')
            return jsonify({"message": "get support by id", "data": normalpayload}), 200
        else:
            return jsonify({"error": "Support ticket not found"}), 404

    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'getsupportdetails.py')
        return jsonify({"error": f"{str(e)}"}), 500
