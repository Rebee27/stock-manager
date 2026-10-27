import sqlite3

def init_db():
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    
    # create product tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    # Add a test product to the database
    cursor.execute('''
        INSERT INTO products (name, quantity, price) 
        VALUES ('Hârtie A4', 50, 25.50)
    ''')
    
    conn.commit()
    conn.close()
    print("The database was successfully created!")

if __name__ == '__main__':
    init_db()