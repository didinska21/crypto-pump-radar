# Crypto Pump Radar

> **Misi:** menemukan koin yang *berpotensi* pump **sebelum** kerumunan beli —
> masuk duluan, keluar dengan disiplin. Bukan menebak. **Mengolah data.**

Repo ini adalah otak risetnya: screener early-entry + pipeline data +
**learning loop**. Setiap sinyal yang discan — lolos *dan* ditolak — dicatat,
dilabeli hasilnya (pump / rug / datar), lalu dipakai untuk mempertajam skor.
Semakin banyak data yang diolah, semakin pintar sistem membedakan
"koin mau terbang" dari "koin mau rug".

Sejak v2, otaknya bekerja sebagai **sistem multi-agent: agent memerintah
agent**. Satu **Komandan** memerintah tujuh agen spesialis (Scout, Auditor,
Analis, Eksekutor, Pengamat, Pelajar, Pelapor) lewat bus perintah yang
memeriksa setiap perintah — penerbit sah, belum kedaluwarsa, tidak ganda,
rantai persetujuan lengkap. Auditor memegang **veto mutlak** atas gate
keamanan; Eksekutor hanya bergerak atas perintah sah Komandan.
Rinciannya: `docs/10-sistem-multi-agent.md` + `docs/11-protokol-perintah.md`,
implementasinya `src/commander.py` + `src/agents.py`.

---

## Cara sistem ini belajar (inti repo)

```
SCAN ──► GATE ──► SKOR ──► CATAT ──► LABEL HASIL ──► OLAH ──► BOBOT BARU
(pool    (aman/   (0-100)  (signals  (+2x? -30%?     (learn.py  (scoring
 baru)    tidak)           .csv)     rug? datar?)     statistik)  v berikutnya)
   ▲                                                              │
   └──────────────── skor makin akurat ◄──────────────────────────┘
```

1. **Scan** — pool baru ditarik dari GeckoTerminal / DexScreener tiap putaran.
2. **Gate keamanan** — honeypot, pajak, LP, konsentrasi holder, kontrak.
   Satu gagal = tolak. Skor **tidak pernah** mengalahkan gate.
3. **Skor komposit 0–100** — dari fitur momentum + keamanan + smart money
   (lihat `docs/04-scoring-model.md`). Skor ≥ 80 = **Tier A**.
4. **Catat semuanya** — termasuk yang ditolak dan alasannya (`data/schema.md`).
   Data yang ditolak sama berharganya: dari situlah pola rug dipelajari.
5. **Label hasil** — harga koin dicek lagi setelah 1j / 6j / 24j / 7h
   (`src/label_outcomes.py`): PUMP (≥ +100%), NAIK, DATAR, TURUN, RUG (≤ −50%
   atau likuiditas hilang).
6. **Olah & belajar** — `src/learn.py` menghitung fitur mana yang benar-benar
   memprediksi PUMP vs RUG, mengusulkan bobot skor baru, dan memperbarui
   `knowledge/pattern-library.md`. Bobot tidak berubah otomatis — di-review,
   di-backtest, baru diadopsi. Disiplin di atas emosi, juga untuk modelnya.

## Fondasi yang sudah jalan (bukan mulai dari nol)

Repo ini berdiri di atas operasi live **Sniper & Screener BSC** (sejak 3 Nov 2026):

| Aset | Status |
|---|---|
| Screener BSC (`sniper.py`, GeckoTerminal + GoPlus + honeypot.is) | LIVE, scan tiap 15 menit |
| Dataset sinyal | **484+ baris** sejak 3 Nov 2026 (skor, keputusan, alasan tolak) |
| Radar smart money (`smartmoney.py`) | LIVE info-only, profil wallet ESTABLISHED / FRESH / CONTRACT |
| Jalur Analisa Momentum | LIVE — skor ≥ 65 + bukti momentum ≥ 2/4 sinyal + semua gate lolos |
| Eksekusi | Agentic Wallet (`baw`), entry $1, maks 2 posisi, SL −30%, target 2x |

Pelajaran awal dari data itu sudah dituangkan di `knowledge/lessons-learned.md`.

## Peta repo

| Folder | Isi |
|---|---|
| `docs/` | Metodologi lengkap: filosofi early-entry, sumber sinyal, gate, model skor, kamus fitur, pipeline data, learning loop, manajemen risiko, roadmap, **sistem multi-agent (10)** dan **protokol perintah (11)** |
| `src/` | Kode yang bisa jalan: `ingest.py`, `features.py`, `scoring.py`, `label_outcomes.py`, `learn.py` + **rantai komando `commander.py` & `agents.py`** + `config/weights.json` & `config/agents.json` |
| `data/` | Skema dataset + template CSV (data mentah live tetap di mesin operasi, bukan di repo) |
| `knowledge/` | Otak yang tumbuh: pattern library (pola pump vs pola rug), lessons learned, peta narasi, glosarium |
| `research/` | Template riset 1 koin — cara meneliti kandidat manual sebelum masuk watchlist |

## Prinsip yang tidak berubah

- **Angka dulu, opini kemudian.** Tidak ada "kayaknya naik". Ada fitur, skor, dan bukti.
- **Gate > skor > narasi.** Koin seviral apa pun ditolak bila gate keamanan gagal.
- **Ragu = batal.** Lebih baik kehilangan peluang daripada kehilangan modal.
- **Modal receh, disiplin sniper.** Ukuran posisi kecil; yang dilindungi pertama adalah modal + gas.
- **Tidak ada janji profit.** Sistem ini menaikkan *probabilitas* dan *kecepatan deteksi*, bukan menghilangkan risiko. Token yang lolos semua gate tetap bisa rug.

## Mulai cepat (kode)

```bash
cd src
python3 scoring.py --demo          # nilai 2 contoh sinyal dengan bobot aktif
python3 commander.py --demo        # satu putaran rantai komando + uji protokol perintah
python3 label_outcomes.py --help   # labeli sinyal lama dari data harga
python3 learn.py --help            # olah outcomes -> statistik pola + usul bobot
```

Bobot skor hidup di `src/config/weights.json` — satu-satunya file yang diubah
learning loop (lewat review), supaya perubahan "kepintaran" sistem selalu
bisa dilacak di git history.

---

*Dibangun 6 Nov 2026 sebagai proyek riset pendamping operasi Sniper BSC.
Repo publik — berisi strategi riset; data live, kunci, dan kredensial
tidak pernah masuk repo.*
