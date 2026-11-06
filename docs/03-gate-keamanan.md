# 03 — Gate Keamanan (Satu Gagal = Tolak)

Gate adalah pagar mutlak yang diwarisi dari SOP Sniper BSC (IDENTITY.md).
Skor setinggi apa pun tidak bisa menebus satu gate yang gagal.

| # | Gate | Batas | Sumber |
|---|---|---|---|
| 1 | Umur pool | 25 menit – 72 jam | GeckoTerminal |
| 2 | Honeypot | flag = 0 + simulasi beli/jual sukses | GoPlus + honeypot.is (2 sumber) |
| 3 | Pajak beli/jual | ≤ 10% | GoPlus |
| 4 | LP tidak terkunci | ≤ 20% (alamat burn dikecualikan = terkunci permanen) | GoPlus `lp_holders` |
| 5 | Jumlah holder | ≥ 8 (dan pertumbuhan organik dipantau sebagai fitur) | GoPlus |
| 6 | Dev menimbun | creator ≤ 10%, owner ≤ 10% | GoPlus |
| 7 | Konsentrasi | top1 non-LP ≤ 10%, top10 ≤ 40% | GoPlus holders |
| 8 | Kontrak | open source; tidak mintable / blacklist / proxy berbahaya / pausable / take-back / hidden owner | GoPlus |
| 9 | Likuiditas | ≥ $10.000 | GeckoTerminal |
| 10 | Gas & saldo | gas pulang-pergi ≤ 15% modal; saldo gas ≥ ambang STANDBY | RPC + saldo wallet agen |

## Kenapa gate seketat ini

Dari 484 sinyal awal operasi (3–6 Nov 2026), **Tier A = 0** di kebanyakan hari.
Itu bukan kegagalan — itu gate bekerja. Alasan tolak terbanyak yang tercatat:

- `holders<8` — token terlalu sepi/belum terindeks.
- `honeypot_is_pair_not_found` — pair belum terindeks honeypot.is → tidak bisa
  diverifikasi = tidak bisa dipercaya.
- `creator 100%` — dev memegang seluruh suplai awal.
- `lp_unlocked>20%`, `top1_holder>10%` — rug tinggal tunggu waktu.

## Watchlist & cek ulang

Kandidat berskor ≥ 80 yang gugur **hanya** karena indeks belum siap
(bukan karena bahaya) masuk watchlist dan dinilai ulang tiap putaran sampai
umur pool 72 jam. Gate tidak berubah selama cek ulang — yang ditunggu hanya
datanya matang, bukan standarnya turun.

## Yang tetap di luar gate

- **Pegangan lama** (bukan hasil screening) tidak disentuh screener.
- Token dari chain lain dicatat sebagai riset; eksekusi saat ini hanya BSC
  via Agentic Wallet sampai ada mandat chain baru.
