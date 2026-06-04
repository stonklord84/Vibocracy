from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import os
# session is the authentication & security tool for when redirect(url_for()) has to be used

app = Flask(__name__)
CORS(app)
app.secret_key = 'secret_key'
socketio = SocketIO(app)

@socketio.on('join')
def on_join(data):
    room = data['room_id']
    join_room(room)
    print(f"user joined room: {room}")

@socketio.on('send_message')
def handle_message(data):
    room = data['room_id']
    msg_text = data['message']
    username = session.get('username', 'Anonymous')

    emit('receive_message', {
        'message': msg_text,
        'username': username
    },to=room)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'appdata', 'data.db')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html", loginstatus='hidden')
    elif request.method == 'POST':
        conn = sqlite3.connect(DB_DIR)
        cursor = conn.cursor()
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            cursor.execute("SELECT password FROM users WHERE username=?;", (username,))
            result = cursor.fetchone()
            if result is None or result[0] != password:
                return render_template('login.html', loginstatus='block')
            cursor.execute("SELECT id FROM users WHERE username=?;", (username,))
            user_id = cursor.fetchone()[0]
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('dashboard'))
        finally:
            conn.close()

@app.route('/api/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect(DB_DIR)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?);", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.rollback()
            return render_template('register.html', usernamestatus='block')
        finally:
            conn.close()
    return render_template('register.html', usernamestatus='hidden')

@app.route('/api/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user_id = session['user_id']
    current_username = session['username']
    conn = sqlite3.connect(DB_DIR)
    cursor = conn.cursor()
    if request.method == "GET":
        cursor.execute("SELECT id, room_name FROM chatrooms WHERE owner_id=?;", (current_user_id,))
        raw_owned_rooms = cursor.fetchall()
        cursor.execute("SELECT room_id, invite_status FROM room_members WHERE user_id=?;", (current_user_id,))
        raw_membership_rooms = cursor.fetchall()
        owned_rooms_id = [id[0] for id in raw_owned_rooms]
        curated_membership_rooms = []
        for membership_room in raw_membership_rooms:
            if membership_room[0] not in owned_rooms_id:
                cursor.execute("SELECT room_name FROM chatrooms WHERE id=?;", (membership_room[0],))
                #n is room name
                n = cursor.fetchone()[0]
                curated_membership_rooms.append((membership_room[0], n, membership_room[1]))

    return render_template('dashboard.html', current_username=current_username, current_owned_rooms = raw_owned_rooms,
                           current_membership_rooms = curated_membership_rooms)

@app.route('/api/create_chatroom', methods=['POST'])
def create_chatroom():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == "GET":
        return redirect(url_for('login'))
    elif request.method == "POST":
        conn = sqlite3.connect(DB_DIR)
        cursor = conn.cursor()
        room_name = request.form.get("roomname")
        cursor.execute("INSERT INTO chatrooms (room_name, vibe_rule, owner_id) VALUES (?, ?, ?);", (room_name, 'free for all', session['user_id']))
        new_room_id = cursor.lastrowid
        cursor.execute("INSERT INTO room_members (room_id, user_id, invite_status) VALUES (?, ?, ?);", (new_room_id, session['user_id'], 'accepted'))
        conn.commit()
        conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/api/delete_chatroom/<int:room_id>', methods=['POST'])
def delete_chatroom(room_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        conn = sqlite3.connect(DB_DIR)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chatrooms WHERE id=?;", (room_id,))
        cursor.execute("DELETE FROM room_members WHERE room_id=?;", (room_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/api/invite/<int:room_id>', methods=['POST'])
def invite_user(room_id):
    if request.method=="POST":
        conn = sqlite3.connect(DB_DIR)
        cursor = conn.cursor()
        invite_username = request.form.get("invite_username")
        print('invite:', invite_username)
        cursor.execute("SELECT user_id FROM room_members WHERE room_id=?;", (room_id,))
        members = cursor.fetchall()
        members = [member[0] for member in members]
        cursor.execute("SELECT id FROM users")
        all_users = cursor.fetchall()
        all_users = [user[0] for user in all_users]
        cursor.execute("SELECT id FROM users WHERE username=?;", (invite_username,))
        invite_user_id = cursor.fetchone()
        if invite_user_id:
            if invite_user_id[0] not in members:
                cursor.execute("INSERT INTO room_members (room_id, user_id, invite_status) VALUES (?, ?, ?);", (room_id, invite_user_id[0], 'pending'))
            else:
                print('this user is already in the room')
        else:
            print('such a user does not exist!')
    conn.commit()
    return redirect(url_for('chatroom', room_id=room_id))

@app.route('/api/respond_to_invite/<int:room_id>', methods=['POST'])
def respond_to_invite(room_id):
    if request.method=="POST":
        conn = sqlite3.connect(DB_DIR)
        cursor = conn.cursor()
        action = request.form.get("action")
        if action == 'accept':
            print(session['user_id'], room_id, action)
            cursor.execute("UPDATE room_members SET invite_status = ? WHERE user_id = ? AND room_id = ?;", 
                           ('accepted', session['user_id'], room_id))
        elif action == 'reject':
            cursor.execute("DELETE FROM room_members WHERE user_id = ? AND room_id = ?;", (session['user_id'], room_id))
        conn.commit()
        return redirect(url_for('dashboard'))

@app.route('/chatroom/<int:room_id>') #must have <int:room_id> in order for it to show up in param
def chatroom(room_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB_DIR)
    cursor = conn.cursor()
    # Find the room name associated with the ID that was clicked
    cursor.execute("SELECT room_name FROM chatrooms WHERE id=?;", (room_id,))
    room_name = cursor.fetchone()[0]
    cursor.execute("SELECT owner_id FROM chatrooms WHERE id=?;", (room_id,))
    room_owner_id = cursor.fetchone()[0]
    is_room_owner = False
    if room_owner_id == session['user_id']:
        is_room_owner = True
    return render_template("chatroom.html", room_name=room_name, room_id=room_id, is_room_owner=is_room_owner)

if __name__ == "__main__":
    #app.run(debug=True, port=5000)
    socketio.run(app, debug=True)