# 08 — Manajemen Risiko (Modal Receh, Disiplin Sniper)

Early entry tanpa manajemen risiko = cara cepat menghabiskan modal kecil.
Aturan ini diwarisi dari SOP operasi dan mengikat semua riset di repo ini.

## Aturan modal (live)

| Aturan | Nilai |
|---|---|
| Ukuran entry | $1 per posisi |
| Posisi terbuka maks | 2 |
| Belanja maks per hari | $2 |
| Stop harian | PnL −$1 → berhenti |
| Stop-loss per posisi | −30% → jual, tanpa diskusi |
| Target | Modal keluar di ±2x |
| Jam tenang | 00:00–06:00 WIB tanpa entry baru (exit darurat tetap boleh) |

## Kondisi STANDBY (tidak menembak sama sekali)

- Saldo gas < ambang minimum operasi.
- Gas pulang-pergi > 15% modal (gwei melonjak).
- 3 kegagalan eksekusi beruntun (fail_streak ≥ 3).
- Posisi sudah 2/2 atau limit harian habis.

## Exit darurat (kapan pun, mengalahkan semua aturan lain)

- Rug terdeteksi: likuiditas turun > 50% atau harga turun > 50% mendadak.
- Kontrak berubah jahat (owner mengaktifkan fungsi berbahaya pasca-entry).
- Simulasi jual gagal / honeypot muncul belakangan.

## Risiko yang diterima secara sadar

- Low-cap bisa −100% dalam menit. Ukuran $1 membuat satu kegagalan tidak fatal.
- Data publik bisa terlambat/salah — karena itu dua sumber keamanan + simulasi
  sebelum eksekusi apa pun.
- Sistem belajar bisa salah arah bila data sedikit — karena itu perubahan bobot
  lewat backtest + review, bukan otomatis.

## Yang tidak akan pernah dilakukan

- Menambah ukuran posisi untuk "balas dendam" setelah rugi (martingale = mati).
- Melonggarkan gate karena "sayang, koinnya lagi viral".
- Memegang koin yang sudah jelas rug demi harapan.
- Memakai wallet utama. Eksekusi hanya wallet agen dengan modal kerja terbatas.
