from flask import Blueprint, jsonify,request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deleteequipmentbp = Blueprint('deleteequipmentbp',__name__)

@deleteequipmentbp.route('/ops/deleteequipment',methods=['POST'])
def deleteequipmentfn():
    equipmentid = str(request.form.get('equipmentid'))
    try:
        db = get_db_connection()
        equipmentcollection = db['equipments']
        equipment = equipmentcollection.find_one({"uid":equipmentid})
        if equipment:
            equipmentcollection.delete_one({"uid":equipmentid})
            generatelogs("info","Equipment deleted successfully","deleteequipment.py")
            return jsonify({"message":"Equipment deleted successfully"})
        else:
            generatelogs("error","Equipment details not found",'deleteequipment.py')
            return jsonify({"message":"Equipment details not found with the id"})
    except Exception as e:
        print(e)
        generatelogs("error",f'{str(e)}','deleteequipment.py')
        return jsonify({"message":f"{str(e)}"})