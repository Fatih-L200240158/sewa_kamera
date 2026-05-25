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
        
        # Ambil semua data pengguna seperti rute katalog
        cursor.execute("SELECT * FROM pengguna")
        semua_user = cursor.fetchall()
        cursor.close()
        
        user_ditemukan = None
        
        # LAKUKAN PENGECEKAN YANG AMAN UNTUK SEGALA JENIS LIBRARY MySQL
        for baris in semua_user:
            # Kemungkinan 1: Jika data berupa Dictionary {'username': 'admin_kamera', ...}
            if isinstance(baris, dict):
                if baris.get('username', '').strip() == username.strip():
                    user_ditemukan = baris
                    break
            # Kemungkinan 2: Jika data berupa Tuple/List biasa ('admin_kamera', ...)
            elif isinstance(baris, (tuple, list)):
                # Kita cari apakah teks username yang diketik ada di dalam tuple ini
                if username.strip() in [str(item).strip() for item in baris]:
                    user_ditemukan = baris
                    break

        if user_ditemukan:
            # Ambil nilai hash dan role secara dinamis berdasarkan tipe datanya
            if isinstance(user_ditemukan, dict):
                db_id = user_ditemukan.get('id')
                db_username = user_ditemukan.get('username')
                db_hash = user_ditemukan.get('password_hash')
                db_role = user_ditemukan.get('role')
            else:
                # Jika tuple, biasanya id di indeks 0, username di 1, hash di 2, role di 3
                db_id = user_ditemukan[0]
                db_username = user_ditemukan[1]
                db_hash = user_ditemukan[2]
                db_role = user_ditemukan[3]
            
            # Eksekusi verifikasi password aman Werkzeug
            if db_hash and check_password_hash(db_hash.strip(), password.strip()):
                session['logged_in'] = True
                session['user_id'] = db_id
                session['username'] = db_username
                session['role'] = db_role
                
                flash('Selamat datang kembali!', 'sukses')
                if db_role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('beranda'))

        # Jika tidak cocok atau tidak ditemukan
        flash('Username atau password salah!', 'gagal')
            
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