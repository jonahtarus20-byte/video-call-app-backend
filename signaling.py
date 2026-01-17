from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token
from models import db, Room
from errors import APIError

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_room')
def handle_join_room(data):
    try:
        token = data.get('token')
        room_id = data.get('room_id')

        if not token or not room_id:
            emit('error', {'message': 'Token and room_id are required'})
            return

        # Decode JWT token to get user identity
        decoded = decode_token(token)
        user_id = decoded['sub']

        # Check if room exists and is active
        room = Room.query.filter_by(room_id=room_id, is_active=True).first()
        if not room:
            emit('error', {'message': 'Room not found or inactive'})
            return

        # Join the SocketIO room
        join_room(room_id)
        emit('joined_room', {'room_id': room_id, 'user_id': user_id}, room=room_id)
        print(f'User {user_id} joined room {room_id}')

    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('leave_room')
def handle_leave_room(data):
    try:
        token = data.get('token')
        room_id = data.get('room_id')

        if not token or not room_id:
            emit('error', {'message': 'Token and room_id are required'})
            return

        decoded = decode_token(token)
        user_id = decoded['sub']

        leave_room(room_id)
        emit('left_room', {'room_id': room_id, 'user_id': user_id}, room=room_id)
        print(f'User {user_id} left room {room_id}')

    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('offer')
def handle_offer(data):
    try:
        token = data.get('token')
        room_id = data.get('room_id')
        offer = data.get('offer')

        if not token or not room_id or not offer:
            emit('error', {'message': 'Token, room_id, and offer are required'})
            return

        decoded = decode_token(token)
        user_id = decoded['sub']

        # Relay offer to other participants in the room
        emit('offer', {'offer': offer, 'from': user_id}, room=room_id, skip_sid=True)

    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('answer')
def handle_answer(data):
    try:
        token = data.get('token')
        room_id = data.get('room_id')
        answer = data.get('answer')

        if not token or not room_id or not answer:
            emit('error', {'message': 'Token, room_id, and answer are required'})
            return

        decoded = decode_token(token)
        user_id = decoded['sub']

        # Relay answer to other participants in the room
        emit('answer', {'answer': answer, 'from': user_id}, room=room_id, skip_sid=True)

    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    try:
        token = data.get('token')
        room_id = data.get('room_id')
        candidate = data.get('candidate')

        if not token or not room_id or not candidate:
            emit('error', {'message': 'Token, room_id, and candidate are required'})
            return

        decoded = decode_token(token)
        user_id = decoded['sub']

        # Relay ICE candidate to other participants in the room
        emit('ice_candidate', {'candidate': candidate, 'from': user_id}, room=room_id, skip_sid=True)

    except Exception as e:
        emit('error', {'message': str(e)})
