# Lessons Learned — Jurnal Pelajaran

Kejadian spesifik → kesimpulan. Yang terulang naik kelas jadi pola
di `pattern-library.md`.

## 2026-11-03 — Hari pertama screening: Tier A = 0 itu normal
60 pool discan, 0 Tier A. Penolakan terbanyak: LP unlocked 100%, top1 holder
20%, holder belum terindeks. **Pelajaran:** di pasar pool-baru, "tidak menemukan
apa-apa" adalah hasil yang sehat. Memaksa entry = membeli sampah.

## 2026-11-03 — honeypot.is 404 bukan berarti endpoint rusak
Token sangat baru sering belum punya pair terindeks di honeypot.is (404
"pair not found"), sementara token mapan terverifikasi sehat di endpoint sama.
**Pelajaran:** bedakan "tidak bisa diverifikasi" dari "terbukti berbahaya" —
keduanya tetap REJECT, tapi yang pertama layak dicek ulang (watchlist),
yang kedua dibuang permanen. Lahirlah label `honeypot_is_pair_not_found`.

## 2026-11-04 — Cluster fresh = keraguan, bukan peluang
Lapisan smart-money menemukan kelas FRESH (nonce ≤ 5) sering muncul berkelompok
pada token baru. **Pelajaran:** keraguan yang terstruktur (FRESH_CLUSTER_HIGH)
cukup untuk BATAL — tidak perlu menunggu bukti dump. Sebaliknya ESTABLISHED
juga menangkap bot/CEX, jadi kehadirannya bukan bukti akumulasi cerdas.

## 2026-11-04 — Skor bagus bisa gugur karena data belum matang
Kandidat skor ≥ 80 gugur hanya karena indeks belum siap. **Pelajaran:**
pisahkan "gagal kualitas" dari "gagal waktu". Watchlist cek-ulang otomatis
disetujui Bos: nilai ulang tiap putaran sampai umur pool 72 jam, gate tetap sama.

## 2026-11-06 — 48 sinyal sehari, tetap 0 Tier A
Screening harian menunjukkan mayoritas token baru mati di gate yang sama:
holders<8, pair belum terindeks, creator 100%. **Pelajaran:** distribusi alasan
tolak adalah peta pasar itu sendiri — pasar pool baru memang didominasi token
asal jadi. Keunggulan kita bukan di jumlah temuan, tapi di tidak ikut terbakar.

## 2026-11-06 — Ambang skor boleh lentur, gate tidak
Jalur Analisa Momentum lahir: skor ≥ 65 boleh (dari 80) asal bukti momentum
≥ 2/4 sinyal dan *semua* gate lolos dari data terindeks. **Pelajaran:**
fleksibilitas yang aman adalah fleksibilitas pada *penilaian*, bukan pada
*keamanan*. Data belum terindeks tetap bukan kandidat, seberapa pun menariknya.

---
*Entri baru ditambahkan setiap kejadian berarti: rug yang lolos, pump yang
terlewat, pola baru terlihat, atau kesalahan keputusan yang ketahuan dari label.*
