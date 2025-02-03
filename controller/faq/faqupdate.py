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