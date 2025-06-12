from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'
DATABASE = 'inventory.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user == 'admin' and pw == 'password':
            session['logged_in'] = True
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    conn = get_db()
    cursor = conn.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    return render_template("index.html", items=items)

if __name__ == '__main__':
    app.run(debug=True)
