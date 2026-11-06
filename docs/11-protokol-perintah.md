# 11 — Protokol Perintah

Format dan aturan sahnya perintah antar-agen di Crypto Pump Radar.
Implementasi acuan: `src/commander.py` (bus perintah + Komandan) dan
`src/config/agents.json` (matriks wewenang yang dibaca bus saat runtime).

## Anatomi satu perintah

```json
{
  "order_id": "ord-20261106-0007-a1b2c3",
  "issuer": "KOMANDAN",
  "target": "EKSEKUTOR",
  "kind": "EXECUTE_INTENT",
  "payload": {
    "ca": "0x...",
    "symbol": "GOOD",
    "amount_usd": 1,
    "gate_pass": true,
    "auditor_veto": false,
    "score": 87.1
  },
  "issued_at": 1793966400,
  "expires_at": 1793967300,
  "idempotency_key": "exec-0x...-2026-11-06",
  "approvals": ["AUDITOR_OK", "ANALIS_OK"],
  "status": "ISSUED"
}
```

| Kolom | Aturan |
|---|---|
| `order_id` | Unik, berurutan, tidak bisa dipakai ulang |
| `issuer` | Harus penerbit sah untuk pasangan (target, kind) itu — dicek bus terhadap `config/agents.json` |
| `kind` | Salah satu jenis perintah terdaftar di `config/agents.json` |
| `payload` | Data tugas. Untuk `EXECUTE_INTENT` wajib memuat bukti rantai: `gate_pass`, `auditor_veto`, `score`, `amount_usd` |
| `expires_at` | Perintah kedaluwarsa = **ditolak**, bukan "tetap dijalankan pelan-pelan". TTL bawaan 900 detik |
| `idempotency_key` | Perintah dengan kunci yang sama tidak pernah dieksekusi dua kali — kunci yang sudah dipakai = ditolak |
| `approvals` | Jejak persetujuan rantai yang sudah dikumpulkan sebelum perintah terbit |
| `status` | `ISSUED → ACCEPTED/REJECTED → DONE/FAILED` — semua transisi masuk log perintah |

## Pemeriksaan bus perintah (berurutan, satu gagal = REJECTED)

1. **Penerbit sah?** Issuer harus ada di daftar penerbit sah *dan* matriks
   wewenang harus mengizinkan issuer memerintah target untuk kind itu.
   Scout → Eksekutor selalu ditolak. Analis → Eksekutor selalu ditolak.
2. **Bukan dari luar rantai?** Issuer di luar {BOS, KOMANDAN, agen
   terdaftar} — termasuk nama token, halaman web, tweet, indeks proyek,
   dokumen eksternal — ditolak sebagai **percobaan injeksi**. Konten
   eksternal adalah data, bukan perintah.
3. **Belum kedaluwarsa?** `now < expires_at`.
4. **Belum pernah dieksekusi?** `idempotency_key` belum ada di log.
5. **Khusus `EXECUTE_INTENT` — rantai lengkap?**
   - `gate_pass == true` dan `auditor_veto == false` (veto mengalahkan
     segalanya, termasuk skor sempurna),
   - skor memenuhi ambang jalurnya (Tier A ≥ 80, atau Momentum ≥ 65
     dengan bukti momentum — ambang dibaca dari `config/weights.json`),
   - pagar Komandan lolos: `amount_usd ≤ entry_usd`, posisi terbuka
     `< maks_posisi`, belanja harian + amount `≤ maks_belanja_harian`,
     di luar jam tenang, tidak sedang STANDBY/HALT.
6. **Khusus `EXIT_INTENT`:** bebas jam tenang (exit darurat selalu boleh),
   tetapi tetap wajib perintah Komandan — Pengamat hanya *mengusulkan*.

## Veto

- Veto Auditor bersifat **final di dalam sistem**. Komandan yang tidak
  setuju dengan veto tetap tidak bisa menerbitkan `EXECUTE_INTENT` untuk
  kandidat itu; jalan satu-satunya adalah eskalasi ke Bos, dan keputusan
  Bos tercatat sebagai perintah BOS (bukan sebagai "veto dibatalkan
  diam-diam").
- Veto selalu disertai alasan tertulis (gate mana yang gagal, angka
  buktinya). Veto tanpa alasan = tidak sah, Auditor wajib mengulang
  pemeriksaan.

## Eskalasi & keraguan

```
Agen ragu ──► naik ke Komandan ──► di luar pagar/mandat ──► naik ke Bos
     │                                    │
     └──► selama ragu: BATAL              └──► selama menunggu: tidak ada
          (tidak ada eksekusi)                 eksekusi untuk item itu
```

- Data belum terindeks **bukan** alasan memaksa: kandidat masuk watchlist
  cek ulang, bukan intent eksekusi.
- Kegagalan beruntun (fail_streak ≥ 3 di Eksekutor) memicu Komandan
  menerbitkan `HALT` internal: STANDBY, dilaporkan ke Bos sekali.

## Kill switch

- `HALT` dari BOS menghentikan semua perintah baru seketika, mengalahkan
  semua perintah berjalan yang belum dieksekusi.
- Komandan boleh menerbitkan `HALT` sendiri hanya pada kondisi STANDBY
  terdefinisi (saldo gas di bawah lantai, fail_streak ≥ 3, pagar harian
  habis) — dan wajib melaporkannya.
- Pencabutan `HALT` hanya oleh penerbitnya atau yang lebih tinggi di
  rantai (Bos > Komandan).

## Log perintah

Setiap perintah — diterima *dan* ditolak — ditulis satu baris JSONL:
order_id, issuer, target, kind, status akhir, alasan penolakan bila ada,
dan cap waktu. Log inilah yang membuat rantai komando bisa diaudit dan
yang dibaca Pelajar untuk belajar: perintah yang ditolak sama berharganya
dengan yang dieksekusi, sama seperti sinyal REJECT di dataset.

## Uji protokol

```bash
cd src
python3 commander.py --demo
```

Demo menjalankan satu putaran penuh plus empat serangan protokol:
perintah langsung Scout → Eksekutor, perintah dari issuer eksternal,
perintah kedaluwarsa, dan perintah ganda (idempotency_key sama).
Keempatnya harus berakhir `REJECTED`; kandidat sehat mencapai intent
eksekusi dry-run; kandidat jebakan mati di veto Auditor.
