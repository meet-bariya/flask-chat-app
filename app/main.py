from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, join_room, leave_room, send
import random
from decouple import config
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    while True:
        code = ''
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    return code

@app.route('/', methods=['GET','POST'])
def index():
    session.clear()
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template('index.html', error='Please Enter a name. ', code=code, name=name)
        if join != 'join' and not create:
            return render_template('index.html', error='Please Enter a room code. ', code=code, name=name)

        room = code
        if create != False:

            room = generate_unique_code(6)
            rooms[room] = {"members": 0, "messages": []}

        elif code not in rooms:
            return render_template('index.html', error='Room does not exists, try creating one. ', code=code, name=name)

        session['room'] = room
        session['name'] = name
        return redirect(url_for('room'))
    return render_template('index.html')

@app.route('/room', methods=['GET','POST'])
def room():
    room = session.get('room')
    print(f"Room: {session.get('room')} Name: {session.get('name')}")
    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('index'))

    return render_template("room.html", room=room, messages=rooms[room]["messages"])

@app.route('/login', methods=['GET','POST'])
def login_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

    return render_template('register.html')

@socketio.on("connect")
def connect(auth):
    room = session.get('room')
    name = session.get('name')

    if not room or not name:
        return
    
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    rooms[room]['members'] += 1
    print(f'{name} has joined the room {room}')

@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)

    if room in rooms:
        rooms[room]['members'] -= 1
        if rooms[room]['members'] < 0:
            del rooms[room]

    print(f'{name} has left the room {room}')


@socketio.on('message')
def message(data):
    room = session.get('room')
    if room not in rooms:
        return 
    
    content = {
        'name': session.get('name'),
        'message': data['data'],
        'timestamp': data['timestamp']
    }
    send(content, to=room)
    rooms[room]['messages'].append(content)
    print(f"{session.get('name')} said: {data['data']}")

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True, host='0.0.0.0', port='8000')