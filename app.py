from flask import Flask, render_template, request, redirect
# Flask --> clasa principală a aplicației web
# render_template --> funcția care ne permite să folosim fișiere HTML
# request --> funcția care ne permite să preluăm datele dintr-un formular
# redirect --> funcția care ne permite să redirecționăm utilizatorul către o altă pagină
import sqlite3
# sqlite3 --> modulul care ne permite să lucrăm cu baza de date SQLite

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('stock.db') # deschide conexiunea la baza de date
    conn.row_factory = sqlite3.Row # permite accesarea coloanelor din baza de date ca și cum ar fi atribute ale unui obiect
    return conn # returnează obiectul de conexiune creat

@app.route('/') # accesarea paginii principale a aplicației web
def index():
    conn = get_db_connection() # deschide conexiunea la baza de date
    products = conn.execute('SELECT * FROM products').fetchall() # selecteaza toate produsele din baza de date
    conn.close() # inchide conexiunea la baza de date
    return render_template('index.html', products=products) # returnează fișierul HTML index.html și îi transmite lista de produse ca parametru

# Ruta nouă pentru salvarea datelor din formular
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
    
    return redirect('/') # redirecționează utilizatorul către pagina principală după ce datele au fost salvate

if __name__ == '__main__':
    app.run(debug=True) 