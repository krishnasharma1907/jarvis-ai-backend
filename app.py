from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from ai_client import AIClient
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Must set in Render env vars

# Use relative path for users.json
USERS_FILE = os.path.join(os.getcwd(), 'users.json')

# --- Helpers ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    return redirect(url_for('chat') if 'username' in session else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        users = load_users()
        if username in users and users[username] == password:
            session['username'] = username
            return jsonify({'success': True, 'redirect': url_for('chat')})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        users = load_users()
        if username in users:
            return jsonify({'success': False, 'message': 'Username already exists'})
        users[username] = password
        save_users(users)
        session['username'] = username
        return jsonify({'success': True, 'redirect': url_for('chat')})
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', username=session['username'])

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    username = session['username']
    data = request.json
    user_input = data.get('message')

    try:
        # Initialize AI with user memory file in working directory
        ai = AIClient(username=username)
        response = ai.get_response(user_input)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f"Error: {str(e)}"})

if __name__ == '__main__':
    # Production on Render: host=0.0.0.0, port from env
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
