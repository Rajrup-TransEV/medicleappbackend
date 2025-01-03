import uuid
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
from werkzeug.utils import secure_filename
import base64

# Upload folder setup
UPLOAD_FOLDER = 'uploads/doctorprofilepicture'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB connection setup
def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'patientops/login.py'
        generatelogs(messagetype, message, filelocation)
        raise

updatedoctordata_bp = Blueprint('updatedoctordata_bp', __name__)

@updatedoctordata_bp.route("/doctors/profile/update", methods=["POST"])
def updatedoctordata():
    # Retrieve form data
    doctorid = request.form.get('doctorid')
    fullname = request.form.get('fullname')
    gender = str(request.form.get("gender"))
    address = str(request.form.get('address'))
    dob = str(request.form.get('dob'))
    specialization = str(request.form.get('specialization'))
    qualification = str(request.form.get('qualification'))
    yoe = str(request.form.get('yoe'))
    license_number = str(request.form.get('license_number'))
    email = str(request.form.get('email'))
    phonenumber = str(request.form.get('phonenumber'))

    profile_picture_file = request.files.get('profilepicture')  # Get the uploaded file

    updatedoctordata = {}

    try:
        db = get_db_connection()
        doctor_collection = db['doctors']
        doctor = doctor_collection.find_one({"uid": doctorid})
        if not doctor:
            return jsonify({"error": "Doctor not found!"}), 404
        if fullname is not None:
            updatedoctordata['fullname'] = fullname
        if gender is not None:
            updatedoctordata['gender']=gender
        if address is not None:
            updatedoctordata['address']=address
        if dob is not None:
            updatedoctordata['dob']=dob
        if specialization is not None:
            updatedoctordata['specialization']=specialization
        if qualification is not None:
            updatedoctordata['qualification']=qualification
        if yoe is not None:
            updatedoctordata['yoe']=yoe
        if license_number is not None:
            updatedoctordata['license_number']=license_number
        if email is not None:
            updatedoctordata['email']=email
        if phonenumber is not None:
            updatedoctordata['phonenumber']=phonenumber
        if profile_picture_file:
            filename = secure_filename(profile_picture_file.filename)
            profile_picture_path = os.path.join(UPLOAD_FOLDER, filename)
            profile_picture_file.save(profile_picture_path)
            with open(profile_picture_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                updatedoctordata['profilepicture'] = encoded_string
        doctor_collection.update_one({"uid": doctorid}, {"$set": updatedoctordata})
        return jsonify({"message": "Doctor data updated successfully!","updateddata":updatedoctordata}), 200
    except Exception as e:
        print(e)
        generatelogs('error', f"Error updating doctor data: {str(e)}", 'doctorops/updatedoctordata.py')
        return jsonify({"error": "Internal Server Error!"}), 500