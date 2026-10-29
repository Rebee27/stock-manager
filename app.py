from flask import Flask, render_template, request, redirect, session
# Flask --> clasa principală a aplicației web
# render_template --> funcția care ne permite să folosim fișiere HTML
# request --> funcția care ne permite să preluăm datele dintr-un formular
# redirect --> funcția care ne permite să redirecționăm utilizatorul către o altă pagină
import sqlite3
# sqlite3 --> modulul care ne permite să lucrăm cu baza de date SQLite
import unicodedata

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'cheie_secreta_super_sigura'

def get_db_connection():
    conn = sqlite3.connect('stock.db') # deschide conexiunea la baza de date
    conn.row_factory = sqlite3.Row # permite accesarea coloanelor din baza de date ca și cum ar fi atribute ale unui obiect
    return conn # returnează obiectul de conexiune creat


def normalize_text(text):
    if not text:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', text)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii.lower()

# --- RUTA DE LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')  # 'manager' sau 'user'
        session['user_role'] = role
        return redirect('/')
    return render_template('login.html')

# --- RUTA DE LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('user_role', None)
    return redirect('/login')

# Această funcție creează automat tabelul orders dacă el nu există deja în stock.db
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Apelăm funcția imediat aici, ca să se creeze tabelul la pornirea serverului
init_db()

@app.route('/') # accesarea paginii principale a aplicației web
def index():
    if 'user_role' not in session:
        return redirect('/login')

    raw_search = request.args.get('search', '')  # Preluăm textul căutat
    filter_status = request.args.get('filter', 'all')  # Preluăm filtrul de stoc

    search_query = normalize_text(raw_search)

    conn = get_db_connection()

    query = 'SELECT * FROM products WHERE 1=1'
    params = []

    if filter_status == 'low':
        query += ' AND quantity <= 10'  # Pragul unitar pentru stoc critic (<= 5)
    elif filter_status == 'out':
        query += ' AND quantity = 0'   # Stoc epuizat

    products = conn.execute(query, params).fetchall()
    conn.close()

    if search_query:
        filtered_products = []
        for p in products:
            normalized_product_name = normalize_text(p['name'])
            if search_query in normalized_product_name:
                filtered_products.append(p)
        products = filtered_products

    return render_template('index.html', products=products, product_to_edit=None, search=search_query, filter_status=filter_status)

# Ruta nouă pentru salvarea datelor din formular (Adăugare)
@app.route('/add', methods=['POST'])
def add_product():
    if session.get('user_role') != 'manager':
        return "Acces interzis! Doar managerul poate adăuga produse.", 403

    name = request.form['name'] # preia valoarea câmpului "name" din formular
    quantity = request.form['quantity'] # preia valoarea câmpului "quantity" din formular
    price = request.form['price'] # preia valoarea câmpului "price" din formular

    conn = get_db_connection() # deschide conexiunea la baza de date
    conn.execute('INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)',
                 (name, quantity, price)) # introduce datele în baza de date
    conn.commit() # salvează modificările în baza de date
    conn.close() # inchide conexiunea la baza de date
    
    return redirect('/') # redirecționează utilizatorul către pagina principală

@app.route('/edit/<int:id>')
def edit_product(id):
    if session.get('user_role') != 'manager':
        return "Acces interzis!", 403

    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    product_to_edit = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('index.html', products=products, product_to_edit=product_to_edit)

@app.route('/update/<int:id>', methods=['POST'])
def update_product(id):
    if session.get('user_role') != 'manager':
        return "Acces interzis!", 403

    name = request.form['name']
    quantity = request.form['quantity']
    price = request.form['price']

    conn = get_db_connection()
    conn.execute('UPDATE products SET name = ?, quantity = ?, price = ? WHERE id = ?',
                 (name, quantity, price, id))
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    if session.get('user_role') != 'manager':
        return "Acces interzis!", 403 

    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.context_processor
def inject_low_stock_count():
    try:
        conn = get_db_connection()
        count = conn.execute('SELECT COUNT(*) FROM products WHERE quantity <= 5').fetchone()[0]
        conn.close()
    except:
        count = 0
    return dict(low_stock_count=count)

@app.route('/order/<int:id>', methods=['POST'])
def create_order(id):
    order_qty = int(request.form['order_quantity'])

    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    
    if product and product['quantity'] >= order_qty:
        new_quantity = product['quantity'] - order_qty
        total_price = prder_qty * product['price']

        # 1. Actualizăm stocul produsului
        conn.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_quantity, id))
        
        # 2. Salvăm comanda în istoric
        conn.execute('INSERT INTO orders (product_name, quantity, total_price) VALUES (?, ?, ?)',
                     (product['name'], order_qty, total_price))        
        conn.commit()
    
    conn.close()
    return redirect('/')

@app.route('/orders')
def view_orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)