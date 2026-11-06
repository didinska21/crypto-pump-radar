# 05 — Kamus Fitur & Indikator

Setiap sinyal disimpan sebagai baris fitur. Fitur yang konsisten dicatat =
syarat sistem bisa belajar. Semua fitur dihitung dari data publik on-chain/API.

## A. Fitur keamanan (dari GoPlus + honeypot.is)

| Fitur | Arti | Arah bagus |
|---|---|---|
| `buy_tax`, `sell_tax` | Pajak transaksi % | Rendah (≤ 5% ideal) |
| `is_honeypot` | Tidak bisa dijual | Wajib 0 |
| `lp_unlocked_pct` | % LP tidak terkunci | Rendah |
| `creator_pct`, `owner_pct` | % suplai di tangan dev/owner | Rendah |
| `is_mintable`, `is_proxy`, `can_blacklist`, `transfer_pausable`, `hidden_owner` | Kemampuan jahat kontrak | Semua 0 |
| `holder_count` | Jumlah holder | ≥ 8 gate; ≥ 100 skor penuh |

## B. Fitur konsentrasi

| Fitur | Arti | Arah bagus |
|---|---|---|
| `top1_pct` | % holder terbesar (non-LP, non-burn) | ≤ 5% ideal |
| `top10_pct` | % 10 holder terbesar | ≤ 25% ideal |
| `fresh_holder_pct` | % holder dompet baru (nonce ≤ 5) | Rendah — tinggi = bundle |
| `established_holder_count` | Jumlah holder dompet ESTABLISHED | ≥ 1–2 = sinyal awal |

## C. Fitur momentum (jantung "potensial pump")

| Fitur | Cara hitung | Arah bagus |
|---|---|---|
| `holder_growth_1h` | Δ holder 1 jam terakhir / holder awal | Positif & stabil |
| `volume_mcap_ratio` | Volume 24j / market cap | ≥ 1 = pasar aktif relatif ke ukuran |
| `buy_sell_ratio` | Jumlah/nilai beli ÷ jual (1j/6j) | > 1, ideal 1.3–3 |
| `liquidity_growth` | Δ likuiditas sejak deteksi | Positif tanpa lonjakan 1 dompet |
| `tx_acceleration` | Transaksi 1j terakhir vs rata-rata jam sebelumnya | Naik bertahap, bukan spike 1 menit |
| `price_change_1h/6h` | Perubahan harga | Hijau moderat; sudah +300% = terlambat |
| `unique_buyers_1h` | Pembeli unik 1 jam | Tumbuh bersama holder |

## D. Fitur narasi & sosial (kualitatif → dibuat skor 0–10)

| Fitur | Yang dinilai |
|---|---|
| `narrative_fit` | Kesesuaian tema koin dengan peta narasi panas (`knowledge/narrative-map.md`) |
| `social_growth` | Pertumbuhan follower/member organik (bukan beli bot) |
| `dev_visibility` | Dev publik & aktif menjawab vs anon senyap |
| `dex_boost` | Ada boost/promosi berbayar di DexScreener (perhatian naik, tapi sering = mau distribusi) |

## E. Fitur konteks pasar

| Fitur | Kenapa penting |
|---|---|
| `bnb_price`, `btc_trend` | Pasar merah besar menekan semua low-cap |
| `gas_gwei` | Gas mahal memakan modal receh — bisa jadi alasan STANDBY |
| `hour_wib` | Jam tenang 00:00–06:00 WIB tanpa entry baru (aturan operasi) |

## Label hasil (untuk belajar)

Setelah jendela waktu lewat, tiap kandidat dilabeli dari harga tertingginya:

| Label | Definisi |
|---|---|
| `PUMP` | Naik ≥ +100% dalam 7 hari |
| `NAIK` | +30% s/d +100% |
| `DATAR` | −30% s/d +30% |
| `TURUN` | −30% s/d −50% |
| `RUG` | ≤ −50%, atau likuiditas ditarik / pool mati |

Label inilah "kunci jawaban" yang membuat `learn.py` bisa menilai fitur mana
yang benar-benar berprediksi — bukan yang terasa berprediksi.
