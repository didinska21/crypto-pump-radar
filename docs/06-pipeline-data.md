# 06 — Pipeline Data (Olah Data)

Prinsip: **tidak ada sinyal yang hilang.** Yang ditolak pun disimpan —
sistem belajar dari keduanya.

## Tahap pipeline

```
1 INGEST      Tarik pool baru (GeckoTerminal/DexScreener) tiap putaran scan.
              Simpan mentah: CA, pool, umur, harga awal, likuiditas, volume.
2 ENRICH      Tambahkan data GoPlus (keamanan + holder) & honeypot.is.
              Klasifikasi holder smart-money (ESTABLISHED/FRESH/CONTRACT).
3 FEATURE     Hitung semua fitur di 05-fitur-indikator.md -> satu baris CSV.
4 DECIDE      Gate -> REJECT / lolos; Skor -> Tier A / Tier B / Momentum.
              Keputusan + alasan selalu ditulis (kolom reject_reasons).
5 SNAPSHOT    Untuk kandidat yang dipantau: snapshot harga+likuiditas berkala
              (1j, 6j, 24j, 7h) — bahan label.
6 LABEL       label_outcomes.py memberi label PUMP/NAIK/DATAR/TURUN/RUG.
7 LEARN       learn.py: statistik per fitur per label -> usul bobot + pola baru.
8 REVIEW      Backtest usul bobot di data lama; adopsi = commit weights.json.
```

## Penyimpanan

| Data | Di mana | Masuk repo? |
|---|---|---|
| Sinyal live (signals.csv) | Mesin operasi `~/workspace/bsc-sniper/state/` | Tidak (tumbuh terus, ada data operasional) |
| Skema & template | `data/` repo ini | Ya |
| Snapshot agregat / statistik belajar | `knowledge/` (ringkasan berkala) | Ya |
| Bobot skor | `src/config/weights.json` | Ya — versi git = audit trail |
| Kunci/API key/seed | Tidak pernah di mana pun dalam repo | **Tidak pernah** |

## Kualitas data (aturan keras pipeline)

- **Dedupe by CA + pool** — token yang sama di banyak pool: pakai pool terlikuid.
- **Satu timestamp acuan** — semua waktu dicatat UTC + ditampilkan WIB.
- **Data belum terindeks ≠ data buruk** — tandai `not_indexed`, masukkan
  watchlist cek ulang; jangan paksa jadi REJECT permanen, jangan pula diloloskan.
- **Error API dicatat, bukan disembunyikan** — 429/gagal fetch masuk log error;
  putaran tetap selesai. Statistik belajar harus tahu ada lubang data.
- **Tidak mengarang angka** — fitur yang tidak bisa dihitung = kosong (`null`),
  bukan 0. Nol palsu meracuni pembelajaran.

## Ritme

| Proses | Frekuensi |
|---|---|
| Ingest + feature + decide | Tiap putaran scan (±15 menit) |
| Snapshot & label 1j/6j | Otomatis mengikuti umur kandidat |
| Label final 24j/7h + learn mingguan | 1× / minggu (review pola & bobot) |
| Update pattern library | Setiap learn menemukan pola signifikan / ada rug yang lolos |
