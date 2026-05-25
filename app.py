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
        
        print("=== BYPASS MODE AKTIF ===", flush=True)
        print(f"Mencoba login dengan username: {username}", flush=True)

        # 🚀 JALAN PINTAS SAKTI: Langsung lolos tanpa cek database pengguna!
        if username.strip() == 'admin_kamera' and password.strip() == 'admin123':
            session['logged_in'] = True
            session['user_id'] = 1  # Kita palsukan ID penggunanya
            session['username'] = 'admin_kamera'
            session['role'] = 'admin'  # Kunci role sebagai admin agar lolos proteksi
            
            flash('Selamat datang kembali Admin (Bypass)!', 'sukses')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau password salah! (Bypass Mode)', 'gagal')
            
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