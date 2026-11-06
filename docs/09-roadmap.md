# 09 — Roadmap

## Fase 0 — Fondasi (SELESAI, live di operasi BSC Sniper)

- [x] Screener pool baru BSC + gate keamanan 2 sumber (3 Nov 2026)
- [x] Skor v1 rule-based, Tier A ≥ 80
- [x] Dataset sinyal berjalan (484+ baris)
- [x] Radar smart money info-only (ESTABLISHED/FRESH/CONTRACT)
- [x] Watchlist cek ulang untuk kandidat belum terindeks
- [x] Jalur Analisa Momentum (skor ≥ 65 + bukti 2/4) — 6 Nov 2026
- [x] Repo riset ini dibuat — 6 Nov 2026

## Fase 1 — Pelabelan hasil (berikutnya)

- [ ] `label_outcomes.py` jalan terjadwal: snapshot harga 1j/6j/24j/7h semua kandidat
- [ ] 300+ kandidat berlabel PUMP/NAIK/DATAR/TURUN/RUG
- [ ] Laporan presisi pertama: Tier A vs Tier B vs REJECT — siapa paling sering pump?
- [ ] Pattern library diperbarui dari data berlabel pertama

## Fase 2 — Skor v2 berbobot

- [ ] `scoring.py` repo ini dipakai berdampingan dengan skor v1 (shadow mode)
- [ ] Perbandingan shadow 2 minggu: v2 harus mengalahkan v1 sebelum menggantikan
- [ ] Sub-skor MOMENTUM & SMART_MONEY masuk keputusan Jalur Momentum secara formal
- [ ] `learn.py` menghasilkan usul bobot mingguan + backtest otomatis

## Fase 3 — Jala lebih lebar

- [ ] Watchlist wallet smart money khusus (dompet ESTABLISHED dengan riwayat pump bagus)
- [ ] Sinyal narasi semi-otomatis (tren kata kunci X/Square per tema)
- [ ] Dukungan chain kedua untuk *riset* (Base/Solana) — eksekusi tetap perlu mandat terpisah
- [ ] Dashboard ringkas: sinyal hari ini, Tier A, pola aktif, metrik kepintaran

## Fase 4 — Model statistik (bila data cukup)

- [ ] Dataset ≥ 1.000 kandidat berlabel
- [ ] Model sederhana (regresi logistik / pohon keputusan) sebagai *penasihat* skor —
      bukan pengganti gate, bukan eksekutor
- [ ] Evaluasi kalibrasi skor berkala; publikasi internal "report card" model

## Prinsip roadmap

Setiap fase harus membuktikan diri di data sebelum fase berikutnya dibuka.
Tidak ada fase yang melonggarkan gate keamanan atau aturan modal.
