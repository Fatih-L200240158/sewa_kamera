import os
from dotenv import load_dotenv

# Membaca file .env jika ada (terutama saat kamu running di laptop)
load_dotenv()

class Config:
    # Kunci rahasia untuk mengamankan data Session / Cookie Login
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci_rahasia_sewa_kamera_2024'
    
    # Konfigurasi database dinamis (Membaca Docker di laptop, atau membaca Clever Cloud di Render)
    MYSQL_HOST = os.environ.get('DB_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('DB_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD') or 'rahasia_kamera'
    MYSQL_DB = os.environ.get('DB_NAME') or 'db_sewa_kamera'