from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

createequipmentbp = Blueprint("createequipmentbp",__name__)

@createequipmentbp.route("/ops/createequipment",methods=['POST'])
def createequipmentfn():
    equipmentname = str(request.form.get("equipmentname"))
    equipmentdetails = str(request.form.get("equipmentdetails"))
    vendorname = str(request.form.get("vendorname"))
    vendordetails = str(request.form.get("vendordetails"))
    equipmentvendorassoid = str(request.form.get("equipmentvendorassoid"))
    purchasedat = str(request.form.get("purchasedat"))
    quantity = str(request.form.get("quantity"))
    equipmentprice = str(request.form.get("equipmentprice"))
    totalgst = str(request.form.get("totalgst"))
    tottaltax = str(request.form.get("tottaltax"))

    try:
        db = get_db_connection()
        createequipmentcol = db['equipments']
        uuidx = str(uuid.uuid4())
        createequipmentcol.insert_one({
            "uid":uuidx,
            "equipmentname":equipmentname,
            "equipmentdetails":equipmentdetails,
            "vendorname":vendorname,
            "vendordetails":vendordetails,
            "equipmentvendorassid":equipmentvendorassoid,
            "purchasedat":purchasedat,
            "quantity":quantity,
            "equipmentprice":equipmentprice,
            "totalgst":totalgst,
            "tottaltax":tottaltax
        })

        generatelogs("success","Create equipment details","createequipment.py")
        return jsonify({"message":"Equipment details hasbeen created successfully","data":uuidx})

    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','createequipment.py')
        return jsonify({'error':"Internal server error"}),500