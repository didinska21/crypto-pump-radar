# src — Kode Olah Data

Semua modul Python 3 stdlib murni (tanpa dependensi) — jalan di mana saja
screener operasi jalan.

| Modul | Fungsi | Dokumen |
|---|---|---|
| `ingest.py` | Tarik pool baru GeckoTerminal → baris mentah | `docs/06` tahap INGEST |
| `features.py` | Hitung fitur turunan (rasio, pertumbuhan, sinyal momentum) | `docs/05` |
| `scoring.py` | Skor komposit v2 dari `config/weights.json` | `docs/04` |
| `label_outcomes.py` | Vonis PUMP/NAIK/DATAR/TURUN/RUG dari snapshot harga | `docs/05` Label |
| `label.py` | Jemput snapshot OHLCV GeckoTerminal per sinyal (1j/6j/24j/7h) → label via `label_outcomes.py`, tulis `data/live/labels.csv` (idempoten) | `docs/06` tahap LABEL, `docs/09` Fase 1 |
| `learn.py` | Statistik daya-pisah fitur + hasil per keputusan → bukti usul bobot | `docs/07` |
| `agents.py` | Tujuh agen spesialis: Scout, Auditor (veto mutlak), Analis, Eksekutor (dry-run), Pengamat, Pelajar, Pelapor | `docs/10` |
| `commander.py` | Komandan + bus perintah: memeriksa & mencatat setiap perintah antar-agen, menjalankan siklus putaran | `docs/10`, `docs/11` |
| `shadow.py` | Mode shadow: putar ulang `signals.csv` produksi lewat rantai Komandan (read-only) → vonis per sinyal vs keputusan produksi di `data/live/shadow_log.jsonl` | `docs/10` Status |
| `config/weights.json` | Bobot aktif. Diubah hanya via learning loop + commit | `docs/04`, `docs/07` |
| `config/agents.json` | Matriks wewenang rantai komando + pagar Komandan. Diubah hanya via review + commit | `docs/10`, `docs/11` |

## Uji cepat

```bash
python3 scoring.py --demo
python3 commander.py --demo
python3 shadow.py            # putar ulang semua sinyal produksi (read-only)
python3 label_outcomes.py --demo
python3 label.py --limit 20   # subset uji; tanpa --limit = semua yang jatuh tempo
python3 ingest.py --network bsc --pages 1 | head
python3 learn.py --signals <signals.csv> --outcomes <outcomes.csv>
```

Prinsip kode sama dengan prinsip datanya: tidak mengarang angka
(None, bukan 0), gate tidak diputuskan di modul skor, dan tidak ada
modul di sini yang mengeksekusi transaksi apa pun — Eksekutor di rantai
komando pun **dry-run** (intent tercatat, bukan transaksi; lihat
`docs/10`).
