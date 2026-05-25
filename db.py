import mysql.connector
from flask import current_app, g

def get_db():
    # Menggunakan objek 'g' bawaan Flask untuk menyimpan koneksi selama request aktif
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    # Memberitahu Flask untuk otomatis menutup koneksi setelah selesai merender halaman
    app.teardown_appcontext(close_db)