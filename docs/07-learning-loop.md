# 07 — Learning Loop: Cara Sistem Ini Makin Pintar

Ini bab terpenting repo. "Pintar" di sini bukan sihir — ini akumulasi
keputusan yang dicatat rapi + dievaluasi jujur.

## Loop-nya (berputar terus)

1. **Putuskan dengan aturan hari ini** (gate + bobot aktif).
2. **Catat keputusan + semua fiturnya** — termasuk yang ditolak.
3. **Tunggu & labeli hasilnya** (PUMP / NAIK / DATAR / TURUN / RUG).
4. **Ukur**: fitur & pola mana yang memisahkan PUMP dari RUG?
   - Presisi Tier A: dari yang diloloskan, berapa % benar-benar naik?
   - Kebocoran: adakah RUG yang sempat lolos gate? Kenapa? → gate/pola diperbaiki.
   - Peluang hilang: adakah REJECT yang ternyata PUMP besar? Fitur apa yang
     kita nilai terlalu kejam? (Belajar dari yang ditolak = keunggulan langka.)
5. **Usulkan perubahan** — bobot baru / pola baru / ambang baru, lengkap dengan
   bukti angkanya (berapa sampel, selisih rata-rata fitur antar label).
6. **Backtest** usulan di seluruh data lama. Hanya adopsi bila menang di data
   yang tidak dipakai untuk menyusun usulan (atau minimal tidak kalah + alasan kuat).
7. **Commit** perubahan + alasannya. Versi berikutnya mulai dari sini.

## Tiga lapisan memori sistem

| Lapisan | Isi | File |
|---|---|---|
| Data | Baris sinyal + label hasil | `state/signals.csv` (mesin operasi), skema di `data/schema.md` |
| Pola | Generalisasi yang terbukti berulang | `knowledge/pattern-library.md` |
| Pelajaran | Kejadian spesifik + kesimpulan | `knowledge/lessons-learned.md` |

Aturan promosi: kejadian sekali = pelajaran. Terulang ≥ 3× dengan arah sama =
naik jadi pola. Pola yang terbukti memprediksi = masuk bobot skor.

## Metrik kepintaran (diukur, bukan dirasa)

- **Precision@TierA** — % Tier A yang berakhir PUMP/NAIK. Target naik dari waktu ke waktu.
- **Rug leak rate** — % kandidat lolos gate yang berakhir RUG. Target → 0.
- **Missed pump rate** — % REJECT yang berakhir PUMP. Boleh ada (disiplin memang
  membuang peluang), tapi alasannya harus dipahami.
- **Calibration** — apakah skor 85 benar-benar lebih sering pump daripada skor 65?
  Bila tidak, skornya bohong dan harus diperbaiki.

## Jebakan belajar (wajib dihindari)

- **Overfit ke 1–2 kejadian** — jangan ubah bobot karena satu koin viral.
  Minimal sampel & backtest dulu.
- **Survivorship bias** — hanya meneliti koin yang masih hidup. Karena itu
  yang mati/rug wajib tetap ada di dataset.
- **Mengajari dari data bocor** — fitur harus yang diketahui *saat keputusan*,
  bukan info yang baru muncul sesudahnya.
- **Mengubah aturan di tengah jalan tanpa catatan** — setiap perubahan =
  commit + alasan. Tanpa itu, tidak ada yang bisa dievaluasi.

## Ritme review

- **Harian** — heartbeat operasi: berapa discan, Tier A, ditolak, alasan terbanyak.
- **Mingguan** — `learn.py` jalan, statistik pola diperbarui, usul bobot di-review.
- **Bulanan** — evaluasi metrik kepintaran; roadmap & peta narasi diperbarui.

## Implementasi pelabelan (sejak 6 Nov 2026)

Langkah 3 loop di atas dijalankan `src/label.py`: membaca
`signals.csv` operasi, menjemput OHLCV jam-an GeckoTerminal per pool,
dan memberi label tiap horizon yang sudah jatuh tempo (1j/6j/24j/7h)
memakai vonis `label_outcomes.py`. Hasil persisten di
`data/live/labels.csv` (idempoten — jalan ulang hanya mengisi horizon
yang kurang). Harga awal diambil dari candle yang memuat waktu sinyal
karena `signals.csv` live belum mencatat harga deteksi; likuiditas
historis tidak tersedia dari API publik, jadi kriteria likuiditas
label tidak terisi dari jalur ini — pool tanpa candle sesudah sinyal
dilabeli RUG (`note=no_candles_after_signal`). Cadence yang masuk akal:
tiap jam (menangkap jendela 1j/6j tepat waktu) — lihat `docs/09` Fase 1.
