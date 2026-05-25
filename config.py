import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci_rahasia_sewa_kamera_2024'
    
    # Biarkan tetap membaca os.environ seperti ini!
    HOST = os.environ.get('DB_HOST') or 'localhost'
    USER = os.environ.get('DB_USER') or 'root'
    PASSWORD = os.environ.get('DB_PASSWORD') or 'rahasia_kamera'
    DB = os.environ.get('DB_NAME') or 'db_sewa_kamera'

    # Ini WAJIB dimasukkan agar semua jenis library Flask MySQL bisa membaca datanya
    MYSQL_HOST = HOST
    MYSQL_USER = USER
    MYSQL_PASSWORD = PASSWORD
    MYSQL_DB = DB

    MYSQL_DATABASE_HOST = HOST
    MYSQL_DATABASE_USER = USER
    MYSQL_DATABASE_PASSWORD = PASSWORD
    MYSQL_DATABASE_DB = DB