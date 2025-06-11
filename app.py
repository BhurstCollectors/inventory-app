from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import csv
import os

app = Flask(__name__)
DB_NAME = 'inventory.db'

TEMPLATE_HOME = '''
<h1>Inventory System</h1>
<a href="/add">Add Inventory</a> | <a href="/remove">Remove Inventory</a> | <a href="/export">Export to CSV</a>
<table border="1">
<tr><th>Barcode</th><th>Name</th><th>Cost</th><th>Quantity</th></tr>
{% for item in items %}
<tr><td>{{ item[0] }}</td><td>{{ item[1] }}</td><td>{{ item[2] }}</td><td>{{ item[3] }}</td></tr>
{% endfor %}
</table>
'''

TEMPLATE_FORM = '''
<h1>{{ action }} Inventory</h1>
<form method="post">
    Barcode: <input type="text" name="barcode" autofocus required><br>
    {% if show_fields %}
    Name: <input type="text" name="name" required><br>
    Cost: <input type="number" step="0.01" name="cost" required><br>
    {% endif %}
    Quantity: <input type="number" name="quantity" required><br>
    <input type="submit" value="Submit">
</form>
<a href="/">Back to Inventory</a>
'''

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS inventory (
                            barcode TEXT PRIMARY KEY,
                            name TEXT,
                            cost REAL,
                            quantity INTEGER
                        )''')

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        items = conn.execute("SELECT * FROM inventory").fetchall()
    return render_template_string(TEMPLATE_HOME, items=items)

@app.route('/add', methods=['GET', 'POST'])
def add_inventory():
    if request.method == 'POST':
        barcode = request.form['barcode']
        quantity = int(request.form['quantity'])
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM inventory WHERE barcode = ?", (barcode,))
            item = cur.fetchone()
            if item:
                cur.execute("UPDATE inventory SET quantity = quantity + ? WHERE barcode = ?", (quantity, barcode))
            else:
                name = request.form['name']
                cost = float(request.form['cost'])
                cur.execute("INSERT INTO inventory VALUES (?, ?, ?, ?)", (barcode, name, cost, quantity))
        return redirect(url_for('index'))
    return render_template_string(TEMPLATE_FORM, action='Add', show_fields=True)

@app.route('/remove', methods=['GET', 'POST'])
def remove_inventory():
    if request.method == 'POST':
        barcode = request.form['barcode']
        quantity = int(request.form['quantity'])
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE inventory SET quantity = quantity - ? WHERE barcode = ?", (quantity, barcode))
        return redirect(url_for('index'))
    return render_template_string(TEMPLATE_FORM, action='Remove', show_fields=False)

@app.route('/export')
def export():
    with sqlite3.connect(DB_NAME) as conn:
        items = conn.execute("SELECT * FROM inventory").fetchall()
    filename = 'inventory_export.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Barcode', 'Name', 'Cost', 'Quantity'])
        writer.writerows(items)
    return f"Exported to {filename}. <a href='/'>Back</a>"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
