# 04 — Model Skor Komposit (0–100)

Skor menjawab satu pertanyaan: *di antara yang AMAN, mana yang paling
berpotensi bergerak?* Skor tidak pernah membuka gate yang gagal.

## v1 — Rule-based (live sejak 3 Nov 2026)

Mulai dari 100, potong proporsional terhadap jarak ke batas gate
(implementasi live: `sniper.py::score`, operasi BSC Sniper):

| Faktor | Potongan maks |
|---|---|
| Pajak tertinggi (beli/jual) /10% | −15 |
| LP unlocked /20% | −10 |
| Creator % /10% | −8 |
| Owner % /10% | −8 |
| Top1 holder /10% | −10 |
| Top10 holder /40% | −10 |
| Holder < 100 | −8 |
| Likuiditas < $50rb | −10 |
| Umur pool < 60 menit | −5 |

**Skor ≥ 80 + semua gate lolos = Tier A** → kandidat entry.

## Jalur Momentum (live sejak 6 Nov 2026)

Untuk kandidat yang analisanya menunjukkan potensi naik ±1 hari–1 minggu:

- Ambang skor dilonggarkan ke **≥ 65** — hanya skornya.
- Semua gate keamanan tetap wajib lolos penuh dari data terindeks.
- Wajib bukti momentum konkret **minimal 2 dari 4**:
  1. pertumbuhan holder/buyer jelas,
  2. rasio volume/mcap ≥ 1 atau volume melonjak,
  3. tekanan beli dominan (buy > sell),
  4. smart money ESTABLISHED hadir (dan **tidak** ada cluster FRESH).

## v2 — Weighted features (target repo ini)

Skor dipecah jadi tiga sub-skor berbobot yang hidup di `src/config/weights.json`:

```
SKOR = w_aman × KEAMANAN + w_momentum × MOMENTUM + w_smart × SMART_MONEY
```

- **KEAMANAN** — turunan v1 (pajak, LP, konsentrasi, likuiditas, umur).
- **MOMENTUM** — fitur baru: pertumbuhan holder, volume/mcap, buy pressure,
  pertumbuhan likuiditas, percepatan transaksi.
- **SMART_MONEY** — kehadiran & kualitas holder ESTABLISHED, penalti cluster FRESH.

Implementasi: `src/scoring.py` (membaca bobot dari JSON — ubah bobot tanpa ubah kode).

## v3 — Belajar dari data (arah roadmap)

Setelah outcomes berlabel cukup banyak (target ≥ 300 kandidat berlabel):

1. `learn.py` menghitung, per fitur, rata-rata nilai pada PUMP vs RUG.
2. Fitur dengan daya pisah besar → bobot naik; fitur yang ternyata noise → turun.
3. Usulan bobot baru ditulis sebagai diff ke `weights.json` + ringkasan bukti.
4. **Review manusia/agen wajib** sebelum adopsi + backtest pada data lama:
   bobot baru harus mengalahkan bobot lama di data historis, bukan cuma terlihat bagus.
5. Setiap perubahan bobot = satu commit git. "Kepintaran" sistem bisa diaudit.

Prinsip: model boleh mengusulkan, disiplin yang memutuskan. Tidak ada
auto-update bobot tanpa backtest — itu cara tercepat mengajari sistem kebiasaan buruk.
