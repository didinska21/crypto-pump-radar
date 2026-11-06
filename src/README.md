# src — Kode Olah Data

Semua modul Python 3 stdlib murni (tanpa dependensi) — jalan di mana saja
screener operasi jalan.

| Modul | Fungsi | Dokumen |
|---|---|---|
| `ingest.py` | Tarik pool baru GeckoTerminal → baris mentah | `docs/06` tahap INGEST |
| `features.py` | Hitung fitur turunan (rasio, pertumbuhan, sinyal momentum) | `docs/05` |
| `scoring.py` | Skor komposit v2 dari `config/weights.json` | `docs/04` |
| `label_outcomes.py` | Vonis PUMP/NAIK/DATAR/TURUN/RUG dari snapshot harga | `docs/05` Label |
| `learn.py` | Statistik daya-pisah fitur + hasil per keputusan → bukti usul bobot | `docs/07` |
| `config/weights.json` | Bobot aktif. Diubah hanya via learning loop + commit | `docs/04`, `docs/07` |

## Uji cepat

```bash
python3 scoring.py --demo
python3 label_outcomes.py --demo
python3 ingest.py --network bsc --pages 1 | head
python3 learn.py --signals <signals.csv> --outcomes <outcomes.csv>
```

Prinsip kode sama dengan prinsip datanya: tidak mengarang angka
(None, bukan 0), gate tidak diputuskan di modul skor, dan tidak ada
modul di sini yang mengeksekusi transaksi apa pun.
