from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
import base64

# Upload folder setup
UPLOAD_FOLDER = 'uploads/doctorprofilepicture'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB connection setup
def get_db_connection():
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db

updatedoctordata_bp = Blueprint('updatedoctordata_bp', __name__)

@updatedoctordata_bp.route("/doctors/updatedata", methods=["POST"])
def getdoctordetaillsbyid():
    doctorid = str(request.form.get('doctorid'))

    # Check if a new profile picture is being uploaded
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        print(f"Uploaded file: {file.filename}")  # Debug log

        try:
            filename = f"{doctorid}_profile_picture.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            print(f"Attempting to save file at: {filepath}")  # Debug log
            
            # Save the file in binary mode
            with open(filepath, "wb") as img_file:
                img_file.write(file.read())
                print("File saved successfully.")  # Debug log

            if os.path.exists(filepath):
                print("File exists after saving.")  # Debug log
            else:
                print("File does NOT exist after saving!")  # Debug log

            # Update MongoDB with new profile picture path
            db = get_db_connection()
            doctor_collection = db['doctors']
            print(f"Updating MongoDB with profile picture path: {filepath}")  # Debug log
            
            result = doctor_collection.update_one(
                {"uid": doctorid},
                {"$set": {"profilepictures": filepath}}
            )
            
            # print(f"MongoDB update result: {result.modified_count}")  # Debug log

            # if result.modified_count == 0:
            #     return jsonify({"error": "Doctor not found or profile picture not updated"}), 404

        except Exception as e:
            messagetype = 'error'
            message = f"Error while uploading profile picture: {str(e)}"
            filelocation = 'doctorsops/getdoctordetailsbyid.py'
            generatelogs(messagetype, message, filelocation)
            return jsonify({"error": str(e)}), 500

    try:
        db = get_db_connection()
        doctor_collection = db['doctors']
        doctor = doctor_collection.find_one({"uid": doctorid})
        
        if not doctor:
            return jsonify({"error": "Doctor not found!"}), 404
        
        leave_collection = db['doctorleave']
        doctor_leave = leave_collection.find_one({"doctorid": doctorid})
        
        leavefrom = doctor_leave.get('leavefrom') if doctor_leave else None
        leaveto = doctor_leave.get('leaveto') if doctor_leave else None
        reason = doctor_leave.get('reason') if doctor_leave else None
        status = doctor_leave.get('status') if doctor_leave else None
        
        profile_picture_path = doctor.get('profilepictures')
        
        if profile_picture_path and os.path.exists(profile_picture_path):
            with open(profile_picture_path, "rb") as img_file:
                profile_picture_data = base64.b64encode(img_file.read()).decode('utf-8')
        else:
            profile_picture_data = None
            
        normal_payload = {
            "uid": doctor.get('uid'),
            "fullname": doctor.get('fullname'),
            "gender": doctor.get('gender'),
            "address": doctor.get('address'),
            "dob": doctor.get('dob'),
            "specialization": doctor.get('specialization'),
            "qualification": doctor.get('qualification'),
            "yoe": doctor.get('yoe'),
            "license_number": doctor.get('license_number'),
            "email": doctor.get('email'),
            "phonenumber": doctor.get('phonenumber'),
            "status": status,
            "leavefrom": leavefrom,
            "leaveto": leaveto,
            "reason": reason,
            "profilepictures": profile_picture_data,
            "role": doctor.get('userrole')
        }
        generatelogs('success',"Doctor data has been fetched successfully",'updatedoctordata.py')
        return jsonify({"message":"Doctor data has been fetched successfully", "data": normal_payload}), 200
    
    except Exception as e:
        messagetype = 'error'
        message = f"Error while fetching doctor data: {str(e)}"
        filelocation = 'doctorsops/updatedoctordata.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": str(e)}), 500
