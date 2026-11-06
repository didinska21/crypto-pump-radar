# Pattern Library — Pola Pump vs Pola Rug

Pola = generalisasi yang teramati berulang (≥ 3 kejadian searah) dari data.
Setiap pola dicatat dengan bukti & tanggal. Pola yang gugur kebenarannya
ditandai GUGUR, bukan dihapus — sejarah kesalahan juga pelajaran.

## Pola PUMP (potensi naik)

### P-01 · Akumulasi diam-diam
Holder ESTABLISHED mulai masuk saat volume masih kecil; holder tumbuh stabil
1–3%/jam; harga datar-menguat pelan. Sering mendahului gerak besar 6–48 jam.
*Bukti awal: kerangka smart-money radar, 4 Nov 2026 — menunggu data berlabel.*

### P-02 · Volume mendahului harga
Rasio volume/mcap menembus ≥ 1 sementara harga baru naik < 30%.
Pasar memanaskan mesin sebelum harga bergerak. Salah satu dari 4 sinyal
resmi Jalur Momentum (live 6 Nov 2026).

### P-03 · Tekanan beli organik
Buy/sell ratio 1.3–3 dengan pembeli unik bertambah (bukan 1 dompet wash-trading).
Beda tipis dengan P-05 di bawah — kuncinya di *keunikan* pembeli.

### P-04 · Narasi tepat waktu
Token selaras tema yang sedang dicari pasar (lihat `narrative-map.md`) +
tiga sinyal di atas. Narasi sendirian TIDAK cukup — narasi + data = kandidat.

## Pola RUG / HINDARI (terbukti dari data operasi)

### R-01 · Cluster dompet fresh
Banyak holder adalah dompet nonce ≤ 5 yang muncul bersamaan = bundle insider.
Pola klasik: pump semu lalu dump serentak. Di operasi: **FRESH_CLUSTER_HIGH = BATAL**.
*Bukti: SMARTMONEY_NOTES, 4 Nov 2026.*

### R-02 · Dev pegang suplai
Creator/owner > 10% (kasus ekstrem teramati: creator 100%).
Satu tombol jual dari dev mengakhiri segalanya.
*Bukti: alasan tolak terbanyak di 484 sinyal awal.*

### R-03 · LP terbuka lebar
LP unlocked > 20% → likuiditas bisa ditarik kapan pun. Rug paling mekanis.

### R-04 · Konsentrasi ekstrem
Top1 non-LP > 10% atau top10 > 40% → distribusi belum selesai; pembeli awal
hanya menunggu exit liquidity.

### R-05 · Wash pump
Volume besar tapi pembeli unik sedikit & holder tidak tumbuh.
Harga digerakkan dompet sendiri untuk memancing FOMO. Lawan dari P-03.

### R-06 · Belum terindeks = belum bisa dipercaya
Pair tak ditemukan di honeypot.is / data GoPlus kosong. Bukan bukti jahat —
tapi tanpa verifikasi, keputusan yang benar adalah menunggu (watchlist),
bukan masuk. *Bukti: `honeypot_is_pair_not_found`, alasan tolak terbanyak kedua.*

## Cara menambah pola

1. Catat kejadian di `lessons-learned.md` dengan CA + tanggal + angka.
2. Bila terulang ≥ 3× searah → usulkan pola baru di sini (format sama:
   nama, deskripsi, bukti).
3. Bila pola memengaruhi keputusan → cerminkan ke fitur/bobot lewat
   proses di `docs/07-learning-loop.md` (backtest dulu).
