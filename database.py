import sqlite3

database = sqlite3.connect('wallpapers.db')
cursor = database.cursor()

cursor.executescript('''
    CREATE TABLE IF NOT EXISTS categories(
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name VARCHAR(50) UNIQUE
    );
    
    CREATE TABLE IF NOT EXISTS images(
        image_id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_link TEXT,
        category_id INTEGER REFERENCES categories(category_id)
    ); 
''')
database.commit()
database.close()


