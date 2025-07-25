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

createpackagebp = Blueprint('createpackagebp', __name__)

@createpackagebp.route("/ops/createpackage", methods=['POST'])
def createpackagefn():
    try:
        # Get form values
        packagename = str(request.form.get("packagename"))
        packageprice_raw = request.form.get("packageprice")
        discount_raw = request.form.get("discount")
        testincludedtitle = str(request.form.get("testincludedtitle"))
        testincludeddescription = str(request.form.get("testincludeddescription"))
        testincludes_raw = request.form.get("testincludes")  # comma-separated string
        faqmessage = str(request.form.get("faqmessage"))

        # Convert and validate price/discount
        packageprice = float(packageprice_raw)
        discount = float(discount_raw)
        finalprice = packageprice - (packageprice * (discount / 100))

        # Split the test includes into a list, strip extra whitespace
        testincludes = [item.strip() for item in testincludes_raw.split(",") if item.strip()]

        # Generate UUID
        packageid = str(uuid.uuid4())

        # Connect to DB
        db = get_db_connection()
        packagecol = db['packages']

        # Insert package
        packagecol.insert_one({
            "packageid": packageid,
            "packagename": packagename,
            "packageprice": packageprice,
            "discount": discount,
            "finalprice": finalprice,
            "testincludedtitle": testincludedtitle,
            "testincludeddescription": testincludeddescription,
            "testincludes": testincludes,
            "faqmessage": faqmessage,
            "created_at": datetime.now(pytz.utc),
            "updated_at": datetime.now(pytz.utc)
        })

        generatelogs('info', 'Package created successfully', 'hcarepackage/createpackage.py')
        return jsonify({"message": "Package created successfully", "finalprice": finalprice}), 200

    except Exception as e:
        generatelogs('error', f'{str(e)}', 'hcarepackage/createpackage.py')
        return jsonify({"error": "internal server error please check logs for details`"}), 500
