from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

updateequipmentbp = Blueprint('updateequipmentbp',__name__)

@updateequipmentbp.route("/ops/updatedata",methods=['POST'])
def updateequipmentfn():
    equipmentid = str(request.form.get('equipmentid'))
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

    updatefields = {}
    if equipmentname is not None:
        updatefields['equipmentname'] = equipmentname
    if  equipmentdetails is not None:
        updatefields['equipmentdetails']=equipmentdetails
    if vendorname is not None:
        updatefields['vendorname'] = vendorname
    if vendordetails is not None:
        updatefields['vendordetails'] = vendordetails
    if equipmentvendorassoid is not None:
        updatefields['equipmentvendorassoid'] = equipmentvendorassoid
    if purchasedat is not None:
        updatefields['purchasedat'] = purchasedat
    if quantity is not None:
        updatefields['quantity'] = quantity
    if equipmentprice is not None:
        updatefields['equipmentprice'] = equipmentprice
    if totalgst is not None:
        updatefields['totalgst'] = totalgst
    if tottaltax is not None:
        updatefields['tottaltax'] = tottaltax
    try:
        db = get_db_connection()
        equipmentcol = db['equipments']
        result = equipmentcol.update_one({"uid":equipmentid},{"$set":updatefields})
        generatelogs("info","Equipment details hasbeen updated successfully","updateequipmentdetails.py")
        return jsonify({"message":"Equipment details hasbeen updated successfully","data":updatefields})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','updateequipmentdetails.py')
        return jsonify({"message":"Internal server error"}),500