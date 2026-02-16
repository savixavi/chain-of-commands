from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "finvertex_internal_secure_key"

# Global state for administrative override
debug_mode = False

def query_db(name_input):
    """Direct concatenation vulnerability for blackbox discovery"""
    conn = sqlite3.connect('hr_portal.db')
    c = conn.cursor()
    query = f"SELECT name, position FROM employees WHERE name = '{name_input}'"
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return rows

# --- Authentication & Tab Routing ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = sqlite3.connect('hr_portal.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return "Error: Username in use."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('hr_portal.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect(url_for('index'))
        return "Authentication Failed."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    global debug_mode
    debug_mode = False
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('index.html', username=session['user'])

@app.route('/<page>')
def static_pages(page):
    """Dynamic routing for sidebar tabs"""
    if 'user' not in session: return redirect(url_for('login'))
    try:
        return render_template(f'{page}.html', username=session['user'])
    except:
        return redirect(url_for('index'))

# --- Interactive Bot Logic ---

@app.route('/chat', methods=['POST'])
def chat():
    global debug_mode
    user_input = request.json.get("message", "")
    user_input_low = user_input.lower()

    # Blackbox Override Trigger
    if "system override" in user_input_low or "ignore previous instructions" in user_input_low:
        debug_mode = True
        return jsonify({"reply": "STATUS: Administrative session active. Security parameters bypassed."})

    # Standard filter (Active until overridden)
    sensitive_terms = ["salary", "pay", "money", "flag", "secret", "credential"]
    if not debug_mode and any(term in user_input_low for term in sensitive_terms):
        return jsonify({"reply": "ACCESS DENIED: Insufficient permissions for requested data node."})

    # Realistic filler responses
    if "hello" in user_input_low or "hi" in user_input_low:
        return jsonify({"reply": "System Ready. How can I assist you today?"})
    
    if "office" in user_input_low:
        return jsonify({"reply": "Main office is at 44 Corporate Way. HQ Hours: 08:00 - 18:00."})

    # Vulnerable Query Path
    try:
        results = query_db(user_input)
        if results:
            return jsonify({"reply": f"Record Found: {results[0][0]} - {results[0][1]}"})
        else:
            return jsonify({"reply": "Query completed. 0 results found in public directory."})
    except Exception as e:
        # The classic Blackbox clue: The raw error message
        return jsonify({"reply": f"INTERNAL_DB_ERROR: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
