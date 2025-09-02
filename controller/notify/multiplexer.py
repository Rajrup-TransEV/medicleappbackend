from datetime import datetime, timezone
import uuid
from flask import request
import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from utils.logs import generatelogs
from dotenv import load_dotenv
from flask_socketio import emit
import json

load_dotenv()

# --- singleton Mongo client ---
_mongo_client = None
def _client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(os.getenv('MONGODB_URI'))
    return _mongo_client

def get_db_connection():
    db = _client()[os.getenv('DB_NAME')]
    # Ensure helpful indexes (run once; PyMongo is idempotent here)
    try:
        db.multiplexer.create_index([('user_id', ASCENDING), ('socket_id', ASCENDING)], unique=True, name='uniq_user_socket')
        db.multiplexer.create_index([('user_id', ASCENDING), ('active', ASCENDING)], name='user_active_idx')
    except Exception as e:
        generatelogs('error', f'Index creation failed: {e}', 'multiplexer.py')
    return db

def _now_utc():
    return datetime.now(timezone.utc)

def _extract_user_id(data):
    # Normalize payload and pull user id from 'user_id' or 'userid'
    if isinstance(data, dict):
        return data.get('user_id') or data.get('userid')
    if isinstance(data, str):
        try:
            obj = json.loads(data)
            return obj.get('user_id') or obj.get('userid')
        except json.JSONDecodeError:
            return None
    # As a last resort (not ideal for WebSocket), try query args
    return request.args.get('user_id')

def multiplexer(socketio):
    @socketio.on('multiplexer')
    def multiplexerfn(data):
        try:
            db = get_db_connection()
            socket_id = request.sid

            generatelogs('debug', f"Socket ID from request.sid: {socket_id}", 'multiplexer.py')
            generatelogs('debug', f"Raw data received: {data}", 'multiplexer.py')

            user_id = _extract_user_id(data)
            if not user_id:
                generatelogs('error', "No user_id provided", 'multiplexer.py')
                emit('error', {'message': 'User ID is required'})
                return

            # TODO: VERIFY AUTH: tie user_id to a verified token/session before trusting it.

            generatelogs('debug', f"User ID retrieved: {user_id}", 'multiplexer.py')

            now = _now_utc()

            # 1) Deactivate any other active sockets for this user
            db.multiplexer.update_many(
                {'user_id': user_id, 'active': True, 'socket_id': {'$ne': socket_id}},
                {'$set': {'active': False, 'disconnection_time': now}}
            )

            # 2) Upsert this exact (user_id, socket_id) so first-time connect ALWAYS saves socket_id
            try:
                db.multiplexer.update_one(
                    {'user_id': user_id, 'socket_id': socket_id},
                    {
                        '$setOnInsert': {
                            'uid': str(uuid.uuid4()),
                            'user_id': user_id,
                            'socket_id': socket_id,
                        },
                        '$set': {
                            'connection_time': now,
                            'active': True,
                            'updated_at': now,
                        }
                    },
                    upsert=True
                )
            except DuplicateKeyError:
                # In case of race, retry a simple set
                db.multiplexer.update_one(
                    {'user_id': user_id, 'socket_id': socket_id},
                    {'$set': {'connection_time': now, 'active': True, 'updated_at': now}}
                )

            # 3) Log whether this was first-time or reconnect
            existing_active = db.multiplexer.find_one({'user_id': user_id, 'socket_id': socket_id})
            if existing_active and existing_active.get('connection_time') == now:
                generatelogs('info', f"First-time connection for User {user_id} with socket ID {socket_id}", 'multiplexer.py')
            else:
                generatelogs('info', f"Reconnected User {user_id} with socket ID {socket_id}", 'multiplexer.py')

            emit('connection_success', {
                'message': 'Connected to multiplexer',
                'user_id': user_id,
                'socket_id': socket_id
            })

            if isinstance(data, dict):
                generatelogs('info', f"Received multiplexer data from user {user_id}: {data}", 'multiplexer.py')

        except Exception as e:
            generatelogs('error', f"Error in multiplexer: {str(e)}", 'multiplexer.py')
            emit('error', {'message': f'Connection failed: {str(e)}'})

    @socketio.on('disconnect')
    def handle_disconnect():
        try:
            socket_id = request.sid
            db = get_db_connection()
            db.multiplexer.update_one(
                {'socket_id': socket_id, 'active': True},
                {'$set': {'active': False, 'disconnection_time': _now_utc()}}
            )
            generatelogs('info', f"User disconnected with socket ID {socket_id}", 'multiplexer.py')
        except Exception as e:
            generatelogs('error', f"Error in disconnect: {str(e)}", 'multiplexer.py')

 