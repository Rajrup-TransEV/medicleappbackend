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

package_update_bp = Blueprint("package_update_bp", __name__)

@package_update_bp.route("/ops/updatepackage", methods=['POST'])
def updatepackagefn():
    try:
        packageid = request.form.get('packageid')
        if not packageid:
            return jsonify({"error": "Missing packageid"}), 400

        # Fetch form data
        packagename = request.form.get("packagename")
        packageprice_raw = request.form.get("packageprice")
        discount_raw = request.form.get("discount")
        testincludedtitle = request.form.get("testincludedtitle")
        testincludeddescription = request.form.get("testincludeddescription")
        testincludes_raw = request.form.get("testincludes")  # comma-separated string
        faqmessage = request.form.get("faqmessage")

        db = get_db_connection()
        packagecol = db['packages']

        # Fetch existing package (to recalculate price if needed)
        existing_package = packagecol.find_one({"packageid": packageid})
        if not existing_package:
            return jsonify({"error": "Package not found"}), 404

        # Build update fields
        updatefields = {}

        if packagename:
            updatefields['packagename'] = packagename
        if packageprice_raw:
            updatefields['packageprice'] = float(packageprice_raw)
        if discount_raw:
            updatefields['discount'] = float(discount_raw)
        if testincludedtitle:
            updatefields['testincludedtitle'] = testincludedtitle
        if testincludeddescription:
            updatefields['testincludeddescription'] = testincludeddescription
        if testincludes_raw:
            updatefields['testincludes'] = [item.strip() for item in testincludes_raw.split(",") if item.strip()]
        if faqmessage:
            updatefields['faqmessage'] = faqmessage

        # Handle price + discount recalculation
        price = updatefields.get('packageprice', existing_package.get('packageprice', 0.0))
        discount = updatefields.get('discount', existing_package.get('discount', 0.0))
        finalprice = price - (price * (discount / 100))
        updatefields['finalprice'] = round(finalprice, 2)

        # Update timestamp
        updatefields['updated_at'] = datetime.now(pytz.utc)

        # Perform the update
        result = packagecol.update_one(
            {"packageid": packageid},
            {"$set": updatefields}
        )

        if result.modified_count == 0:
            return jsonify({"message": "No changes made (data may be identical)"}), 200

        generatelogs('info', f'Package {packageid} updated successfully', 'hcarepackage/updatepackage.py')
        return jsonify({"message": "Package updated successfully"}), 200

    except Exception as e:
        generatelogs('error', str(e), 'hcarepackage/updatepackage.py')
        return jsonify({"error": "internal server error please check logs for details"}), 500
