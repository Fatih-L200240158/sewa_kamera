// script.js - Interaksi Frontend Aplikasi Sewa Kamera

// Fungsi 1: Otomatis menghilangkan notifikasi pesan flash setelah 4 detik
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        let flash = document.querySelector('.flash-pesan');
        if(flash) {
            flash.style.transition = 'opacity 0.5s';
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        }
    }, 4000);
});

// Fungsi 2: Pop-up simulasi pemesanan kamera di halaman katalog
function sewaKamera(namaKamera) {
    alert("Sistem Booking Terdeteksi!\n\nAnda memilih untuk menyewa: " + namaKamera + ".\nFitur transaksi langsung lewat web ini sedang dalam tahap pengembangan tugas.");
}