from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash # Untuk cek password aman
from config import Config
import db

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi jembatan database
db.init_app(app)

# 1. RUTE: BERANDA
@app.route('/')
def beranda():
    return render_template('beranda.html')

# 2. RUTE: KATALOG KAMERA
@app.route('/katalog')
def katalog():
    koneksi = db.get_db()
    cursor = koneksi.cursor(dictionary=True) # dictionary=True agar output berupa nama kolom
    
    # Ambil semua data kamera dari database
    cursor.execute("SELECT * FROM kamera")
    data_kamera = cursor.fetchall()
    cursor.close()
    
    return render_template('katalog.html', daftar_kamera=data_kamera)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        koneksi = db.get_db()
        cursor = koneksi.cursor()
        
        # KUNCI URUTAN: 0=id, 1=username, 2=password_hash, 3=role
        cursor.execute("SELECT id, username, password_hash, role FROM pengguna")
        semua_user = cursor.fetchall()
        cursor.close()
        
        user_ditemukan = None
        
        for baris in semua_user:
            if isinstance(baris, dict):
                if baris.get('username', '').strip() == username.strip():
                    user_ditemukan = baris
                    break
            else:
                elemen_str = [str(item).strip() for item in baris]
                if username.strip() in elemen_str:
                    user_ditemukan = baris
                    break

        if user_ditemukan:
            if isinstance(user_ditemukan, dict):
                db_id = user_ditemukan.get('id')
                db_username = user_ditemukan.get('username')
                db_password_db = user_ditemukan.get('password_hash') # Isinya teks biasa 'admin123'
                db_role = user_ditemukan.get('role')
            else:
                db_id = user_ditemukan[0]
                db_username = user_ditemukan[1]
                db_password_db = user_ditemukan[2] # Isinya teks biasa 'admin123'
                db_role = user_ditemukan[3]
            
            # 🔎 KAMERA PENGINTAI VERSI NON-HASH
            print("=== PENGUJIAN TEKS MENTAH ===", flush=True)
            print(f"Password dari Form: {password.strip()}", flush=True)
            print(f"Password dari DB: {str(db_password_db).strip()}", flush=True)
            
            # 🚀 COCOKKAN LANGSUNG MENGGUNAKAN SAMA DENGAN (==)
            if db_password_db and str(db_password_db).strip() == password.strip():
                session['logged_in'] = True
                session['user_id'] = db_id
                session['username'] = db_username
                session['role'] = db_role
                
                flash('Selamat datang kembali (Murni DB Non-Hash)!', 'sukses')
                if db_role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('beranda'))
            
        flash('Username atau password salah! (Database Mode)', 'gagal')
            
    return render_template('login.html')

# 4. RUTE: DASHBOARD ADMIN (KELOLA STOK)
@app.route('/admin')
def admin_dashboard():
    # Proteksi Halaman: Cek apakah yang masuk beneran admin yang sudah login
    if not session.get('logged_in') or session.get('role') != 'admin':
        flash('Akses ditolak! Anda bukan admin.', 'gagal')
        return redirect(url_for('login'))
        
    koneksi = db.get_db()
    cursor = koneksi.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kamera")
    data_kamera = cursor.fetchall()
    cursor.close()
    
    return render_template('admin.html', daftar_kamera=data_kamera)

# 5. RUTE: TAMBAH KAMERA BARU (AKSI DARI FORM ADMIN)
@app.route('/admin/tambah', methods=['POST'])
def tambah_kamera():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    nama = request.form['nama_kamera']
    merk = request.form['merk']
    tipe = request.form['tipe']
    harga = request.form['harga_per_hari']
    
    koneksi = db.get_db()
    cursor = koneksi.cursor()
    
    # Simpan kamera baru menggunakan Parameterized Query
    query = "INSERT INTO kamera (nama_kamera, merk, tipe, harga_per_hari) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (nama, merk, tipe, harga))
    koneksi.commit()
    cursor.close()
    
    flash('Kamera baru berhasil ditambahkan!', 'sukses')
    return redirect(url_for('admin_dashboard'))

# 6. RUTE: LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah keluar.', 'sukses')
    return redirect(url_for('beranda'))

# 5.1 RUTE: UBAH HARGA KAMERA
@app.route('/admin/ubah/<int:id_kamera>', methods=['POST'])
def ubah_harga(id_kamera):
    # Proteksi keamanan admin
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    harga_baru = request.form['harga_baru']
    
    koneksi = db.get_db()
    cursor = koneksi.cursor()
    
    # Query SQL untuk mengubah harga berdasarkan ID
    query = "UPDATE kamera SET harga_per_hari = %s WHERE id = %s"
    cursor.execute(query, (harga_baru, id_kamera))
    koneksi.commit()
    cursor.close()
    
    flash('Harga kamera berhasil diperbarui!', 'sukses')
    return redirect(url_for('admin_dashboard'))


# 5.2 RUTE: HAPUS KAMERA
@app.route('/admin/hapus/<int:id_kamera>')
def hapus_kamera(id_kamera):
    # Proteksi keamanan admin
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    koneksi = db.get_db()
    cursor = koneksi.cursor()
    
    # Query SQL untuk menghapus data berdasarkan ID
    query = "DELETE FROM kamera WHERE id = %s"
    cursor.execute(query, (id_kamera,))
    koneksi.commit()
    cursor.close()
    
    flash('Kamera berhasil dihapus dari inventaris!', 'sukses')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)