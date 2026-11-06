# 09 — Roadmap

## Fase 0 — Fondasi (SELESAI, live di operasi BSC Sniper)

- [x] Screener pool baru BSC + gate keamanan 2 sumber (3 Nov 2026)
- [x] Skor v1 rule-based, Tier A ≥ 80
- [x] Dataset sinyal berjalan (484+ baris)
- [x] Radar smart money info-only (ESTABLISHED/FRESH/CONTRACT)
- [x] Watchlist cek ulang untuk kandidat belum terindeks
- [x] Jalur Analisa Momentum (skor ≥ 65 + bukti 2/4) — 6 Nov 2026
- [x] Repo riset ini dibuat — 6 Nov 2026

## Fase 1 — Pelabelan hasil (BERJALAN — implementasi 6 Nov 2026)

- [x] Snapshot harga 1j/6j/24j/7h terjadwal: `src/label.py` terimplementasi
      (OHLCV GeckoTerminal per pool → vonis `label_outcomes.py` →
      `data/live/labels.csv`, idempoten). Run penuh pertama 6 Nov 2026:
      487 sinyal terlabeli, 1.376 baris label (1j: 487, 6j: 482, 24j: 407,
      7h: 0 — belum ada sinyal berumur 7 hari; jatuh tempo pertama 10 Nov).
      Cron-nya sendiri belum dipasang — usulan: tiap jam.
- [x] 300+ kandidat berlabel PUMP/NAIK/DATAR/TURUN/RUG — tercapai:
      PUMP 703, RUG 399, DATAR 224, NAIK 47, TURUN 3 (per baris horizon).
      Catatan jujur: PUMP dominan karena definisi repo memakai max gain
      intra-jendela dari baseline close candle jam-an (signals live belum
      mencatat harga deteksi) — baca bersama `note` (647 stale_end,
      148 no_candles_after_signal=RUG).
- [ ] Laporan presisi pertama: Tier A vs Tier B vs REJECT — siapa paling sering pump?
      (Dataset live sejauh ini 100% REJECT; perbandingan Tier menunggu sinyal lolos pertama.)
- [ ] Pattern library diperbarui dari data berlabel pertama

## Fase 2 — Skor v2 berbobot

- [ ] `scoring.py` repo ini dipakai berdampingan dengan skor v1 (shadow mode)
- [ ] Perbandingan shadow 2 minggu: v2 harus mengalahkan v1 sebelum menggantikan
- [ ] Sub-skor MOMENTUM & SMART_MONEY masuk keputusan Jalur Momentum secara formal
- [ ] `learn.py` menghasilkan usul bobot mingguan + backtest otomatis

## Fase 2B — Rantai komando multi-agent (SELESAI di repo, 6 Nov 2026)

- [x] Hierarki agent-memerintah-agent: Bos → Komandan → 7 agen spesialis (`docs/10`)
- [x] Matriks wewenang tertulis di `src/config/agents.json` (siapa boleh memerintah siapa)
- [x] Protokol perintah: format perintah, TTL, idempotency, rantai persetujuan, veto mutlak Auditor, eskalasi, kill switch (`docs/11`)
- [x] Implementasi acuan stdlib: `src/commander.py` (bus perintah + Komandan) & `src/agents.py` — demo putaran + 5 uji serangan protokol lolos (perintah tak sah/kedaluwarsa/ganda/melewati veto semuanya ditolak bus)
- [x] Eksekutor dry-run di repo: intent tercatat & bisa diaudit, tanpa menyentuh uang
- [x] Mode shadow REPLAY historis (6 Nov 2026): `src/shadow.py` memutar ulang 489 sinyal produksi lewat rantai Komandan (read-only, `data/live/shadow_log.jsonl`) — 473 veto Auditor / 14 veto data / 1 veto catatan produksi / 1 lolos tanpa intent / 0 intent; keterbatasan: fitur momentum & smart-money tidak tersimpan di signals.csv sehingga jalur skor belum bisa dinilai shadow
- [ ] Mode shadow di operasi live: Komandan mencatat perintah yang *akan* diterbitkan berdampingan dengan putaran sniper berjalan (±2 minggu perbandingan) — butuh perintah Bos
- [ ] Adopsi live bertahap: rantai komando mengambil alih orkestrasi putaran, pagar SOP tidak berubah

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
