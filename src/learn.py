#!/usr/bin/env python3
"""Otak learning loop: olah signals+outcomes berlabel -> bukti pola.

Untuk setiap fitur numerik, hitung rata-rata pada kelompok PUMP/NAIK
vs RUG/TURUN. Selisih besar & konsisten = fitur berdaya pisah ->
kandidat naik bobot (proses adopsi: docs/07 — backtest + review,
TIDAK otomatis mengubah weights.json).

Juga menghitung metrik kepintaran: precision Tier A, rug leak,
missed pump, dan kalibrasi skor (docs/07).

Pakai:
  python3 learn.py --signals signals.csv --outcomes outcomes.csv
CSV mengikuti skema data/schema.md. Kolom yang kosong diabaikan
per-fitur (pairwise), bukan dianggap 0.
"""
import argparse
import csv
import statistics as st
import sys
from collections import defaultdict

GOOD = {"PUMP", "NAIK"}
BAD = {"RUG", "TURUN"}
FEATURES = ["age_min", "liquidity_usd", "holder_count", "buy_tax", "sell_tax",
            "lp_unlocked_pct", "creator_pct", "owner_pct", "top1_pct",
            "top10_pct", "buy_sell_ratio", "volume_mcap_ratio",
            "established_holders", "fresh_cluster", "score"]


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(row, key):
    v = row.get(key)
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signals", required=True)
    ap.add_argument("--outcomes", required=True)
    a = ap.parse_args()
    signals = {r["ca"]: r for r in load(a.signals) if r.get("ca")}
    final = {}
    for o in load(a.outcomes):  # label horizon terjauh yang menang
        if o.get("ca") and o.get("label"):
            final[o["ca"]] = o["label"]
    joined = [(signals[ca], lab) for ca, lab in final.items() if ca in signals]
    if not joined:
        print("Tidak ada sinyal berlabel yang bisa digabung. "
              "Kumpulkan outcomes dulu (docs/06 tahap LABEL).")
        return 1
    print(f"Sampel berlabel: {len(joined)}  "
          f"(bagus {sum(1 for _, l in joined if l in GOOD)}, "
          f"buruk {sum(1 for _, l in joined if l in BAD)})\n")

    print("DAYA PISAH FITUR (rata-rata BAGUS vs BURUK; selisih besar = berguna)")
    for feat in FEATURES:
        g = [num(r, feat) for r, l in joined if l in GOOD]
        b = [num(r, feat) for r, l in joined if l in BAD]
        g = [x for x in g if x is not None]
        b = [x for x in b if x is not None]
        if len(g) >= 3 and len(b) >= 3:
            print(f"  {feat:22s} bagus={st.mean(g):10.2f} (n={len(g)})  "
                  f"buruk={st.mean(b):10.2f} (n={len(b)})  "
                  f"selisih={st.mean(g) - st.mean(b):+.2f}")

    dec = defaultdict(list)
    for r, l in joined:
        dec[r.get("decision", "?")].append(l)
    print("\nHASIL PER KEPUTUSAN")
    for d, labs in sorted(dec.items()):
        good = sum(1 for l in labs if l in GOOD)
        print(f"  {d:10s} n={len(labs):4d}  bagus {good} "
              f"({good / len(labs) * 100:.0f}%)  rug {labs.count('RUG')}")
    print("\nCatatan: ini BUKTI untuk review, bukan perubahan bobot otomatis. "
          "Adopsi lewat backtest + commit (docs/07).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
