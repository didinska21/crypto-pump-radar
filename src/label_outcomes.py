#!/usr/bin/env python3
"""Labeli hasil kandidat: PUMP / NAIK / DATAR / TURUN / RUG.

Logika label murni dari angka (docs/05 bagian Label):
  RUG   : max drawdown <= -50% ATAU likuiditas akhir ~0/hilang
  PUMP  : max gain >= +100%
  NAIK  : +30% .. +100%
  TURUN : -30% .. -50% (dan bukan RUG)
  DATAR : sisanya

Dipakai atas snapshot harga (1h/6h/24h/7d) yang dikumpulkan pipeline.
Tanpa snapshot, tidak ada label; tanpa label, tidak ada belajar.

Pakai:
  python3 label_outcomes.py --demo
  python3 label_outcomes.py label --start 100 --high 260 --end 210 --liq-end 50000
"""
import argparse


def label(start_price, high_price, end_price, liq_end=None, liq_start=None):
    if not start_price or high_price is None or end_price is None:
        return None
    max_gain = (high_price - start_price) / start_price * 100.0
    end_change = (end_price - start_price) / start_price * 100.0
    liq_gone = liq_end is not None and liq_start and liq_end < 0.05 * liq_start
    if end_change <= -50 or liq_gone:
        return "RUG"
    if max_gain >= 100:
        return "PUMP"
    if max_gain >= 30:
        return "NAIK"
    if end_change <= -30:
        return "TURUN"
    return "DATAR"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    lp = sub.add_parser("label")
    for k in ("start", "high", "end"):
        lp.add_argument(f"--{k}", type=float, required=True)
    lp.add_argument("--liq-end", type=float)
    lp.add_argument("--liq-start", type=float)
    a = ap.parse_args()
    if a.demo:
        cases = [(100, 260, 210, None, None), (100, 140, 135, None, None),
                 (100, 105, 97, None, None), (100, 130, 62, None, None),
                 (100, 180, 30, 100, 50000)]
        for c in cases:
            print(c, "->", label(*c))
    elif a.cmd == "label":
        print(label(a.start, a.high, a.end, a.liq_end, a.liq_start))
    else:
        ap.print_help()
