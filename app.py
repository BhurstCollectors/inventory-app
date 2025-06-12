from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)
DATABASE = "inventory.db"

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

@app.route("/")
def index():
    conn = get_db()
    cursor = conn.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    return render_template("index.html", items=items)

if __name__ == "__main__":
    app.run()
