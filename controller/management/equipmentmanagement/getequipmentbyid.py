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

getallequipmentbyidbp = Blueprint("getallequipmentbyidbp",__name__)

@getallequipmentbyidbp.route("/ops/getallequipmentbyid",methods=['POST'])
def getallequipmentfn():
    equipid = str(request.form.get('equipid'))
    try:
        db = get_db_connection()
        equipmentcol = db['equipments']
        getequipmentdata = equipmentcol.find_one({"uid":equipid})
        normal_payload ={
            "equipmentdbid":getequipmentdata.get('uid'),
            "equipmentname":getequipmentdata.get('equipmentname'),
            "equipmentdetails":getequipmentdata.get('equipmentdetails'),
            "vendorname":getequipmentdata.get('vendorname'),
            "vendordetails":getequipmentdata.get('vendordetails'),
            "equipmentvendorassociatedid":getequipmentdata.get('equipmentvendorassid'),
            "purchasedat":getequipmentdata.get('purchasedat'),
            "quantity":getequipmentdata.get('quantity'),
            "equipmentprice":getequipmentdata.get('equipmentprice'),
            "totalgst":getequipmentdata.get('totalgst'),
            "tottaltax":getequipmentdata.get('tottaltax')
        }
        generatelogs('info','Get equipment by id data fetched','getequipmentbyid.py')
        return jsonify({"message":"Get equipment by id fetched ","data":normal_payload})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getequipmentbyid.py')
        return jsonify({"message":"Internal server error"}),500