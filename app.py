from flask import Flask, render_template, request, redirect
# Flask --> clasa principală a aplicației web
# render_template --> funcția care ne permite să folosim fișiere HTML
# request --> funcția care ne permite să preluăm datele dintr-un formular
# redirect --> funcția care ne permite să redirecționăm utilizatorul către o altă pagină
import sqlite3
# sqlite3 --> modulul care ne permite să lucrăm cu baza de date SQLite

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

def get_db_connection():
    conn = sqlite3.connect('stock.db') # deschide conexiunea la baza de date
    conn.row_factory = sqlite3.Row # permite accesarea coloanelor din baza de date ca și cum ar fi atribute ale unui obiect
    return conn # returnează obiectul de conexiune creat

@app.route('/') # accesarea paginii principale a aplicației web
def index():
    conn = get_db_connection() # deschide conexiunea la baza de date
    products = conn.execute('SELECT * FROM products').fetchall() # selecteaza toate produsele din baza de date
    conn.close() # inchide conexiunea la baza de date

    # search and filter bar
    search_query = request.args.get('search', '')  # Get the search query from the request parameters
    filter_status = request.args.get('filter', 'all')  # Get the filter status from the request parameters

    conn = get_db_connection()

    query = 'SELECT * FROM products WHERE 1=1'  # Base query
    params = []

    if search_query:
        query += ' AND name LIKE ?'
        params.append(f'%{search_query}%')

    if filter_status == 'low':
        query += ' AND quantity < 10'
    elif filter_status == 'out':
        query += ' AND quantity = 0'

    products = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('index.html', products=products, product_to_edit=None, search=search_query, filter_status=filter_status)

# Ruta nouă pentru salvarea datelor din formular (Adăugare)
@app.route('/add', methods=['POST'])
def add_product():
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
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    product_to_edit = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('index.html', products=products, product_to_edit=product_to_edit)

@app.route('/update/<int:id>', methods=['POST'])
def update_product(id):
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
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)