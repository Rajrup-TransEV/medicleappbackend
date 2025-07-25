from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv
from .doctorsearch import search_doctors
from .patientsearch import patientsearch
from .billsearch import billsearch
from .rooms import roomsearch
from .staffsearch import staffsearch
from .appoinmntsearch import appoinmntsearch
from .packagesearch import packagesearch

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]  # e.g., 'medicare'
    return db

searchbp = Blueprint('search', __name__)

@searchbp.route('/search', methods=['POST'])
def searchfn():
    query = (
        request.form.get('search') or 
        (request.json.get('search') if request.is_json else None)
    )

    if not query:
        return jsonify({"message": "Search value must be provided in 'search' field"}), 400

    results = {}

    # Doctor search
    doctors = search_doctors(query)
    if doctors:
        results["doctors"] = doctors

    # Patient search
    patients = patientsearch(query)
    if patients:
        results["patients"] = patients
    
    # Bill search
    bills = billsearch(query)
    if bills:
        results["bills"] = bills

    # Room search
    rooms = roomsearch(query)
    if rooms:
        results["rooms"] = rooms
    
    # Staff search
    staff = staffsearch(query)
    if staff:
        results["staff"] = staff

    # Appoinmnt search
    appoinmnts = appoinmntsearch(query)
    if appoinmnts:
        results["appoinmnts"] = appoinmnts
    
    # Package search
    packages = packagesearch(query)
    if packages:
        results["packages"] = packages

    # Add more sections like labs, pharmacies, etc. as needed
    # labs = labsearchfn(query)
    # if labs:
    #     results["labs"] = labs

    if not results:
        return jsonify({"message": "No results found"}), 404

    return jsonify(results), 200
