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

getallequipmentbp = Blueprint("getallequipmentbp",__name__)

@getallequipmentbp.route('/ops/getallequipment',methods=['GET'])
def getallequipmentfn():
    try:
        db = get_db_connection()
        getallequipmentcol = db['equipments']
        getallequipments = getallequipmentcol.find()
        result = []
        for equipment in getallequipments:
            payloaddata = {
                'uid':equipment.get('uid'),
                "equipmentname":equipment.get('equipmentname'),
                "equipmentdetails":equipment.get('equipmentdetails'),
                "vendorname":equipment.get('vendorname'),
                "vendordetails":equipment.get('vendordetails'),
                "equipmentvendorassoid":equipment.get('equipmentvendorassid'),
                "purchasedat":equipment.get('purchasedat'),
                "quantity":equipment.get('quantity'),
                "equipmentprice":equipment.get('equipmentprice'),
                "totalgst":equipment.get('totalgst'),
                "totaltax":equipment.get("totaltax")
            }
            result.append(payloaddata)
        generatelogs('info','All equipment data hasbeen fetched','getallequipment.py')
        return jsonify({"message":"All equipment data hasbeen fetched successfully","data":result}),200
    except Exception as e:
        print(e)
        generatelogs("error",f"{str(e)}","getallequipment.py")
        return jsonify({"error":f"{str(e)}"}),500