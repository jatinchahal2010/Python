from flask import Flask, render_template_string, request, session, redirect
from flask_socketio import SocketIO, send
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app)

# DB init
def init_db():
    with sqlite3.connect('chat.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, sender TEXT, content TEXT)')
        conn.commit()
init_db()

# Templates ( HTML + CSS + JS )
login_page = '''
<!DOCTYPE html>
<html>
<head>
    <title>Chat Login</title>
    <style>
        body {font-family: Arial; background: linear-gradient(#2193b0, #6dd5ed); display: flex; justify-content: center; align-items: center; height: 100vh;}
        .box {background: white; padding: 30px; border-radius: 10px; width: 300px; text-align: center;}
        input, button {width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ccc;}
        button {background: #2193b0; color: white; border: none;}
        h2 {margin-bottom: 20px;}
    </style>
</head>
<body>
    <div class="box">
        <h2>Welcome to Chat</h2>
        <form action="/login" method="post">
            <input type="text" name="username" placeholder="Username" required/>
            <input type="password" name="password" placeholder="Password" required/>
            <button type="submit">Login</button>
        </form>
        <form action="/register" method="post">
            <input type="text" name="username" placeholder="New Username" required/>
            <input type="password" name="password" placeholder="New Password" required/>
            <button type="submit">Register</button>
        </form>
    </div>
</body>
</html>
'''

chat_page = '''
<!DOCTYPE html>
<html>
<head>
    <title>Chat Room</title>
    <style>
        body {font-family: Arial; background: #f0f2f5; margin: 0; padding: 0;}
        .navbar {background: #2193b0; padding: 15px; color: white; text-align: center; font-size: 20px;}
        .chat-container {max-width: 800px; margin: 20px auto; background: white; border-radius: 8px; overflow: hidden;}
        .messages {height: 400px; overflow-y: scroll; padding: 20px;}
        .input-area {display: flex; padding: 10px; border-top: 1px solid #ccc;}
        .input-area input {flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px;}
        .input-area button {padding: 10px 20px; margin-left: 10px; background: #2193b0; color: white; border: none; border-radius: 4px;}
        .msg {margin-bottom: 15px;}
        .msg span {display: block;}
        .msg .sender {font-weight: bold; color: #333;}
        .msg .content {margin-top: 5px; padding: 10px; background: #e1f5fe; border-radius: 5px;}
        .avatar {width: 30px; height: 30px; border-radius: 50%; vertical-align: middle; margin-right: 10px;}
    </style>
</head>
<body>
    <div class="navbar">Logged in as {{username}} | <a href="/logout" style="color: yellow;">Logout</a></div>
    <div class="chat-container">
        <div class="messages" id="messages">
            {% for sender, content in msgs %}
            <div class="msg">
                <span class="sender"><img src="https://i.pravatar.cc/30?u={{sender}}" class="avatar"/> {{sender}}</span>
                <span class="content">{{content}}</span>
            </div>
            {% endfor %}
        </div>
        <div class="input-area">
            <input type="text" id="msg" placeholder="Type a message...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
<script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
<script>
    var socket = io();
    var input = document.getElementById("msg");
    var box = document.getElementById("messages");

    function sendMessage() {
        let text = input.value.trim();
        if (text !== "") {
            socket.emit("message", text);
            input.value = "";
        }
    }

    socket.on("message", function(data) {
        let msgDiv = document.createElement("div");
        msgDiv.className = "msg";
        msgDiv.innerHTML = '<span class="sender"><img src="https://i.pravatar.cc/30?u=' + data.sender + '" class="avatar"/> ' + data.sender + '</span><span class="content">' + data.msg + '</span>';
        box.appendChild(msgDiv);
        box.scrollTop = box.scrollHeight;
    });
</script>
</body>
</html>
'''

# Routes
@app.route('/')
def home():
    if 'username' in session:
        return redirect('/chat')
    return render_template_string(login_page)

@app.route('/register', methods=['POST'])
def register():
    u, p = request.form['username'], request.form['password']
    try:
        with sqlite3.connect('chat.db') as conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?,?)', (u, p))
            conn.commit()
        session['username'] = u
        return redirect('/chat')
    except:
        return "Username already taken. <a href='/'>Back</a>"

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form['username'], request.form['password']
    with sqlite3.connect('chat.db') as conn:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
    if user:
        session['username'] = u
        return redirect('/chat')
    return "Login failed. <a href='/'>Try again</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect('/')
    with sqlite3.connect('chat.db') as conn:
        msgs = conn.execute('SELECT sender, content FROM messages').fetchall()
    return render_template_string(chat_page, username=session['username'], msgs=msgs)

@socketio.on('message')
def handle_msg(msg):
    sender = session.get('username', 'Guest')
    with sqlite3.connect('chat.db') as conn:
        conn.execute('INSERT INTO messages (sender, content) VALUES (?, ?)', (sender, msg))
        conn.commit()
    send({'sender': sender, 'msg': msg}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
