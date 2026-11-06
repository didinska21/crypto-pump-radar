# 10 — Sistem Multi-Agent (Agent Memerintah Agent)

> Sejak v2 repo ini tidak lagi digambarkan sebagai satu pipeline tunggal,
> melainkan sebagai **rantai komando**: satu **Komandan** yang memerintah
> agen-agen spesialis. Setiap agen punya satu keahlian, wewenang yang
> tertulis, dan batas yang tidak bisa ia langkahi — termasuk Komandan
> sendiri.

## Kenapa rantai komando, bukan satu agen serbabisa

Operasi live membuktikan tiga hal:

1. **Eksekusi harus dipisah dari penilaian.** Agen yang menemukan kandidat
   tidak boleh juga yang memutuskan beli — godaan "kandidatku sendiri"
   adalah bias. Di sini penemu (Scout), penilai keamanan (Auditor),
   penilai peluang (Analis), dan pengeksekusi (Eksekutor) adalah empat
   peran berbeda, dan Eksekutor hanya bergerak atas perintah.
2. **Satu veto harus lebih kuat dari semua antusiasme.** Gate keamanan
   yang bisa dioverride oleh siapa pun yang sedang semangat bukan gate.
   Veto Auditor di sistem ini **mutlak** — bahkan Komandan tidak bisa
   membatalkannya. Hanya Bos yang bisa, dan itu pun tercatat.
3. **Perintah harus bisa diaudit.** Kalau besok ada posisi yang rugi,
   pertanyaannya bukan "siapa yang salah" melainkan "perintah nomor
   berapa, diterbitkan siapa, atas bukti apa". Semua perintah lewat satu
   bus dan tercatat di log perintah — tidak ada perintah lisan antar-agen.

## Hierarki

```
                         BOS
              (mandat, pagar modal & risiko,
               kill switch, satu-satunya di atas veto)
                          │  mandat / HALT
                          ▼
                      KOMANDAN
        (orkestrator — menerjemahkan mandat jadi perintah,
         memeriksa pagar, mengumpulkan persetujuan rantai)
        │        │        │        │        │        │
      SCAN    GATE_    SCORE   EXECUTE  MONITOR   LEARN / REPORT
        ▼      CHECK     ▼      _INTENT     ▼        ▼
      SCOUT    ▼       ANALIS     ▼       PENGAMAT  PELAJAR / PELAPOR
             AUDITOR            EKSEKUTOR
             (VETO              (satu-satunya yang
              mutlak)            menyentuh eksekusi,
                                 hanya atas perintah sah)
```

## Para agen

| Agen | Peran | Boleh memerintah | Ditentukan oleh |
|---|---|---|---|
| **Komandan** | Orkestrator: membagi tugas, memeriksa pagar (cap $1/$2, maks 2 posisi, jam tenang, STANDBY), mengeluarkan intent eksekusi, eskalasi | Semua agen spesialis | Mandat Bos (dokumen ini + `config/agents.json`) |
| **Scout** | Mata: ingest pool/sinyal baru, mengusulkan kandidat | Tidak ada — hanya mengusulkan | `src/ingest.py` |
| **Auditor** | Penjaga gate: memeriksa semua gate keras, memegang **veto mutlak** | Tidak ada — veto adalah hak menolak, bukan memerintah | `docs/03-gate-keamanan.md` |
| **Analis** | Otak skor: skor komposit, momentum, smart money; rekomendasi Tier A / Momentum / Watch | Tidak ada — rekomendasi bukan perintah | `src/scoring.py` + `config/weights.json` |
| **Eksekutor** | Tangan: menjalankan intent eksekusi yang sah dari Komandan. Di repo ini **dry-run** — mengeluarkan intent tercatat, bukan transaksi | Tidak ada | Pagar SOP operasi (entry $1, SL −30%, target 2x) |
| **Pengamat** | Pengawas posisi: memantau harga/likuiditas, mengusulkan exit mekanis & exit darurat | Tidak ada — mengusulkan exit ke Komandan | Aturan exit SOP |
| **Pelajar** | Memori: mencatat semua hasil, melabeli outcome, mengusulkan bobot baru | Tidak ada — usulan bobot lewat review + backtest + commit | `src/learn.py`, `docs/07-learning-loop.md` |
| **Pelapor** | Mulut: Call Card, laporan entry/exit, heartbeat — dari fakta tercatat saja | Tidak ada | Format SOP operasi |

Matriks wewenang yang mengikat hidup di `src/config/agents.json` —
**satu-satunya sumber kebenaran** soal siapa boleh memerintah siapa.

## Siklus satu putaran (rantai persetujuan)

```
1. Komandan ──SCAN──► Scout        : "tarik pool baru cakupan BSC"
2. Scout ──usulan──► Komandan      : daftar kandidat mentah
3. Komandan ──GATE_CHECK──► Auditor: "periksa kandidat X"
4. Auditor ──vonis──► Komandan     : LOLOS, atau VETO + alasan (final)
5. Komandan ──SCORE──► Analis      : (hanya kandidat lolos gate)
6. Analis ──rekomendasi──► Komandan: skor + verdict + bukti momentum
7. Komandan memeriksa pagar        : modal, posisi, jam, STANDBY
8. Komandan ──EXECUTE_INTENT──► Eksekutor (hanya bila 4+6+7 semua hijau)
9. Eksekutor ──hasil──► Komandan   : intent tercatat / (di live: FINISHED/FAILED)
10. Komandan ──MONITOR/REPORT/LEARN──► Pengamat, Pelapor, Pelajar
```

Tidak ada jalan pintas: Scout tidak bisa memerintah Eksekutor, Analis
tidak bisa memerintah Eksekutor, dan "rekomendasi kuat" tidak pernah
melewati Auditor. Format perintah dan aturan sah/tidaknya dirinci di
`docs/11-protokol-perintah.md`; implementasi acuannya di
`src/commander.py` + `src/agents.py` (stdlib, bisa diuji dengan `--demo`).

## Apa yang TIDAK berubah

- **Gate > skor > narasi.** Rantai komando tidak melonggarkan satu gate pun.
- **Ragu = batal** berlaku di setiap agen, bukan hanya Komandan.
- **Eksekusi live tetap di mesin operasi** (Agentic Wallet `baw`, SOP
  sniper). Repo ini adalah otak + buku peraturannya; Eksekutor di sini
  dry-run supaya rantai komando bisa diuji dan diaudit tanpa menyentuh
  uang. Adopsi protokol ini ke operasi live adalah langkah terpisah yang
  butuh perintah Bos dan berjalan bertahap (shadow dulu, baru live).

## Status

- v1 (6 Nov 2026): hierarki, matriks wewenang, protokol perintah, dan
  implementasi acuan (bus perintah + agen) selesai dan teruji lewat demo:
  kandidat sehat mengalir sampai intent eksekusi; kandidat jebakan mati
  di veto Auditor; perintah dari penerbit tak sah, perintah kedaluwarsa,
  dan perintah ganda semuanya ditolak bus.
- Mode shadow REPLAY terimplementasi (6 Nov 2026): `src/shadow.py` memutar
  ulang seluruh `signals.csv` produksi (489 baris) lewat rantai Komandan
  secara read-only — hasil di `data/live/shadow_log.jsonl`. Vonis: 473 veto
  Auditor dari nilai fitur terpulihkan, 14 veto data tak terverifikasi,
  1 veto catatan produksi di luar model repo, 1 lolos gate tanpa intent,
  0 intent — sepakat 100% dengan produksi, TAPI angka itu struktural:
  file produksi 100% REJECT dan fitur momentum/smart-money tidak pernah
  tersimpan di `signals.csv` (kelengkapan nilai pasti rata-rata hanya
  25,3% dari 17 fitur), sehingga skor bayangan mentok di 50 dan jalur
  intent tidak pernah terjangkau. Agar shadow bisa menilai jalur skor,
  screener live perlu mencatat snapshot fitur penuh per sinyal.
- Berikutnya (butuh perintah Bos): mode shadow di operasi live — Komandan
  mencatat perintah yang *akan* ia terbitkan berdampingan dengan putaran
  sniper yang berjalan, dibandingkan selama ±2 minggu sebelum rantai
  komando mengambil alih putaran live.
