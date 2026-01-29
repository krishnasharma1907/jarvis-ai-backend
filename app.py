from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from ai_client import AIClient
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session'  # Verify: Change this in production
USERS_FILE = 'c:/New folder/users.json'

# --- Helpers ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
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
    if 'username' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

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
        # Initialize AI with the specific user's memory
        ai = AIClient(username=username)
        response = ai.get_response(user_input)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
