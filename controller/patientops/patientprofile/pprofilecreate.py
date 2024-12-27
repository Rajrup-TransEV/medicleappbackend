import uuid
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
from werkzeug.utils import secure_filename
import base64

UPLOAD_FOLDER = 'uploads/patientprofilepictures'
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

pprofilecreate_bp = Blueprint('pprofilecreate_bp', __name__)

@pprofilecreate_bp.route("/patients/profile/update", methods=["POST"])
def pprofilecreate():
    # Retrieve form data
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    age = request.form.get('age')
    bloodgroup = request.form.get('bloodgroup')
    weight = request.form.get('weight')
    height = request.form.get('height')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    phonenumber = request.form.get('phonenumber')
    address = request.form.get('address')
    email = request.form.get('email')
    # name = request.form.get('name')

    # Handle file upload
    profilepicture = request.files.get('profilepicture')  # Get the uploaded file
    patientid = str(request.form.get('patientid'))

    update_fields = {}
    
    try:
        db = get_db_connection()
        patient_collection = db['patients']
        patient = patient_collection.find_one({"uid": patientid})

        if not patient:
            return jsonify({"error": "Patient not found!"}), 404
        
        # Update fields only if they are provided and not None
        if firstname is not None:
            update_fields['firstname'] = firstname
        if lastname is not None:
            update_fields['lastname'] = lastname
        if age is not None:
            update_fields['age'] = age
        if bloodgroup is not None:
            update_fields['bloodgroup'] = bloodgroup
        if weight is not None:
            update_fields['weight'] = weight
        if height is not None:
            update_fields['height'] = height
        if gender is not None:
            update_fields['gender'] = gender
        if dob is not None:
            update_fields['dob'] = dob
        if phonenumber is not None:
            update_fields['phonenumber'] = phonenumber
        if address is not None:
            update_fields['address'] = address
        if email is not None:
            update_fields['email'] = email
        # if name is not None:
        #     update_fields['name'] = name
        
        # Handle profile picture upload if provided
        if profilepicture:
            filename = secure_filename(profilepicture.filename)
            uniquefilename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, uniquefilename)

            # Save the profile picture in binary mode
            with open(filepath, 'wb') as img_file:  # Open the file in write-binary mode
                img_file.write(profilepicture.read())  # Write the content of the uploaded file
            
            update_fields['profilepicture'] = filepath  # Save the path to the database

        # Update the patient record in the database only with non-null fields
        result = patient_collection.update_one({"uid": patientid}, {"$set": update_fields})

        # Fetch updated patient data from database after updating it
        updated_patient_data = patient_collection.find_one({"uid": patientid})

        # Prepare updated data including base64 encoded image if available
        updated_data = {
            "firstname": updated_patient_data['firstname'],
            "lastname": updated_patient_data['lastname'],
            "age": updated_patient_data['age'],
            "bloodgroup": updated_patient_data['bloodgroup'],
            "weight": updated_patient_data['weight'],
            "height": updated_patient_data['height'],
            "gender": updated_patient_data['gender'],
            "dob": updated_patient_data['dob'],
            "phonenumber": updated_patient_data['phonenumber'],
            "address": updated_patient_data['address'],
            "email": updated_patient_data['email'],
            # "name": updated_patient_data['name'],
        }

        # Encode profile picture to base64 if it exists in the database
        if 'profilepicture' in updated_patient_data and os.path.exists(updated_patient_data['profilepicture']):
            with open(updated_patient_data['profilepicture'], 'rb') as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
                updated_data['profilepicture'] = encoded_image  # Add base64 image to response

        return jsonify({"message": "Patient profile updated successfully!", "updateddata": updated_data}), 200
   
    except Exception as e:
        generatelogs('error', f'Error occurred: {str(e)}', 'patientops/profile.py')
        return jsonify({"error": "An error occurred while updating the profile."}), 500
