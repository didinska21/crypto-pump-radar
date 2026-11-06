# 01 — Filosofi Early Entry: Beli Sebelum Kerumunan

## Masalah yang dipecahkan

Koin low-cap bergerak dalam fase yang berulang:

```
LAHIR ──► AKUMULASI ──► PERHATIAN ──► FOMO ──► DISTRIBUSI ──► MATI
(pool     (smart money   (volume &     (retail    (whale jual,   (atau
 baru)     masuk diam-    holder naik)  masuk)     harga jatuh)   konsolidasi)
           diam)
   ▲           ▲             ▲
   kita mau masuk di sini — bukan di FOMO
```

Mayoritas retail masuk di fase FOMO (saat koin sudah trending & hijau besar).
Kita berburu di fase **LAHIR → AKUMULASI**: pool baru berumur menit–jam,
likuiditas cukup, holder mulai tumbuh organik, dompet pintar mulai menyentuh —
sebelum koin itu muncul di trending page mana pun.

## Tiga keunggulan yang dikejar

1. **Kecepatan deteksi** — scanner melihat pool baru dalam hitungan menit,
   bukan menunggu viral. Sumber: feed `new_pools`, bukan trending.
2. **Kualitas saringan** — 99% pool baru adalah sampah/rug. Keunggulan bukan
   "menemukan banyak", tapi "menolak dengan benar dan cepat" (gate + skor).
3. **Belajar dari hasil** — setiap keputusan dicatat dan dilabeli. Sistem lain
   lupa; sistem ini ingat. Pola yang terbukti pump diperkuat, pola rug dibuang.

## Apa itu "potensial pump" secara operasional

Bukan firasat. Sebuah koin disebut berpotensi bila **bukti terukur** ini muncul
bersamaan (detail di `05-fitur-indikator.md`):

- Likuiditas cukup & tumbuh (bukan sekali suntik lalu cabut).
- Holder bertambah terus, konsentrasi longgar (bukan 1 dompet pegang 40%).
- Tekanan beli dominan (buy/sell ratio > 1) dengan volume/mcap sehat.
- Dompet ESTABLISHED (smart money) ikut memegang — bukan hanya cluster dompet fresh.
- Narasi koin selaras dengan tema yang sedang dicari pasar (`knowledge/narrative-map.md`).
- Kontrak bersih: tidak bisa di-mint sepihak, tidak bisa di-pause sepihak,
  pajak wajar, LP mayoritas terkunci/burn.

Satu-dua sinyal saja = spekulasi. Empat+ sinyal + gate bersih = kandidat.

## Horizon waktu

- **Deteksi:** menit pertama – 72 jam umur pool.
- **Potensi gerak yang diburu:** ±1 hari – 1 minggu (selaras Jalur Analisa Momentum).
- **Keluar:** mekanis, bukan perasaan — stop-loss −30%, target modal keluar di 2x,
  exit darurat bila rug terdeteksi (likuiditas/harga anjlok > 50%).

## Yang TIDAK dilakukan sistem ini

- Tidak mengejar koin yang sudah pump besar (mengejar = jadi exit liquidity orang).
- Tidak all-in. Ukuran posisi tetap kecil & dibatasi aturan modal.
- Tidak percaya call dari grup/KOL tanpa verifikasi data sendiri.
- Tidak memprediksi harga. Sistem melaporkan **probabilitas & bukti**, bukan ramalan.
