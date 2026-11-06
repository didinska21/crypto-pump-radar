# Skema Dataset

Satu baris = satu kandidat pada satu momen keputusan. Konsistensi kolom =
syarat `learn.py` bisa bekerja.

## `signals.csv` — sinyal saat keputusan

| Kolom | Tipe | Keterangan |
|---|---|---|
| `timestamp` | ISO-8601 UTC | Waktu deteksi/keputusan |
| `symbol` | teks | Simbol token |
| `ca` | alamat | Contract address (tidak pernah dikarang) |
| `pool` | alamat | Alamat pool yang dipakai menilai |
| `chain` | teks | `bsc` (chain lain menyusul) |
| `age_min` | angka | Umur pool (menit) saat deteksi |
| `price_usd` | angka | Harga saat deteksi |
| `liquidity_usd` | angka | Likuiditas pool |
| `mcap_usd` | angka | Market cap (boleh kosong bila tak terhitung) |
| `volume_24h_usd` | angka | Volume 24 jam |
| `holder_count` | angka | Jumlah holder |
| `buy_tax`, `sell_tax` | angka % | Pajak |
| `lp_unlocked_pct` | angka % | LP tak terkunci |
| `creator_pct`, `owner_pct` | angka % | Kepemilikan dev |
| `top1_pct`, `top10_pct` | angka % | Konsentrasi (non-LP, non-burn) |
| `buy_sell_ratio` | angka | Tekanan beli (boleh kosong di v1) |
| `volume_mcap_ratio` | angka | Aktivitas relatif |
| `established_holders` | angka | Holder ESTABLISHED |
| `fresh_cluster` | 0/1 | Indikasi cluster dompet fresh |
| `score` | angka 0–100 | Skor komposit bobot aktif |
| `decision` | teks | `TIER_A` / `TIER_B` / `MOMENTUM` / `REJECT` |
| `reject_reasons` | teks `;`-pisah | Alasan gate gagal (kosong bila lolos) |

Dataset live kompatibel: operasi BSC Sniper sudah menulis kolom inti
(`timestamp,symbol,ca,pool,age_min,liquidity_usd,score,decision,reject_reasons`)
sejak 3 Nov 2026 — kolom tambahan diisi bertahap oleh enrich v2.

## `outcomes.csv` — label hasil

| Kolom | Keterangan |
|---|---|
| `ca` | Menghubungkan ke signals |
| `checked_at` | Waktu snapshot |
| `horizon` | `1h` / `6h` / `24h` / `7d` |
| `price_usd` | Harga saat snapshot |
| `liquidity_usd` | Likuiditas saat snapshot (0/hilang → kandidat RUG) |
| `max_gain_pct` | Kenaikan maksimum sejak deteksi sampai horizon ini |
| `label` | `PUMP` / `NAIK` / `DATAR` / `TURUN` / `RUG` (dari max_gain & kondisi akhir) |

## Aturan data

- Nilai tak terhitung = **kosong**, bukan 0.
- Satu CA bisa punya banyak baris outcomes (per horizon), satu baris signals
  per momen keputusan (re-scan dicatat sebagai baris baru bertimestamp beda).
- Koreksi data salah = baris koreksi + catatan, bukan edit diam-diam,
  supaya riwayat keputusan tetap bisa diaudit.
