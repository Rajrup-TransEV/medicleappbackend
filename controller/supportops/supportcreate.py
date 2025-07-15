from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from werkzeug.utils import secure_filename
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = 'uploads/supportdocs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

supportcreatebp = Blueprint('supportcreatebp', __name__)

@supportcreatebp.route('/ops/supportops', methods=['POST'])
def supportfn():
    name = str(request.form.get('name'))
    email = str(request.form.get('email'))
    phone = str(request.form.get('phone'))
    issuetype = str(request.form.get('issuetype'))
    message = str(request.form.get('message'))

    try:
        db = get_db_connection()
        supportcol = db['support']
        uuidx = str(uuid.uuid4())

        # Handle file uploads (max 5 files)
        uploaded_files = request.files.getlist('documents')
        if len(uploaded_files) > 5:
            return jsonify({"error": "Maximum 5 files are allowed"}), 400

        saved_file_paths = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuidx}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                saved_file_paths.append(filepath)

        supportcol.insert_one({
            "uid": uuidx,
            "name": name,
            "email": email,
            "phone": phone,
            "issuetype": issuetype,
            "message": message,
            "documents": saved_file_paths,
            "created_at": datetime.now(pytz.timezone("Asia/Kolkata"))
        })

        generatelogs('success', "Support created", 'supportcreate.py')
        return jsonify({"message": "Support created", "data": uuidx}), 200

    except Exception as e:
        print(e)
        generatelogs('error', str(e), 'supportcreate.py')
        return jsonify({"error": str(e)}), 500
