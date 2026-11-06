#!/usr/bin/env python3
"""Skor komposit v2 (weighted) untuk Crypto Pump Radar.

Membaca bobot dari config/weights.json. Tiga sub-skor:
  KEAMANAN    — turunan skor v1 operasi BSC Sniper (mulai 100, potong
                proporsional ke batas gate). Kandidat yang GAGAL gate
                tidak dinilai di sini — gate diputuskan pemanggil.
  MOMENTUM    — fitur gerak: volume/mcap, tekanan beli, pertumbuhan
                holder & likuiditas.
  SMART_MONEY — holder ESTABLISHED menambah, cluster FRESH menghabisi.

SKOR = w_aman*KEAMANAN + w_momentum*MOMENTUM + w_smart*SMART_MONEY

Pakai:
  python3 scoring.py --demo
  python3 scoring.py --json '{"buy_tax":1,...}'   # satu sinyal sbg JSON
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEIGHTS = json.loads((HERE / "config" / "weights.json").read_text())


def _f(sig, key, default=0.0):
    v = sig.get(key)
    return default if v is None else float(v)


def keamanan(sig, w):
    d = w["keamanan_deductions"]
    s = 100.0
    tax = max(_f(sig, "buy_tax"), _f(sig, "sell_tax"))
    s -= (tax / 10.0) * d["tax_max"]
    s -= (_f(sig, "lp_unlocked_pct") / 20.0) * d["lp_unlocked_max"]
    s -= (_f(sig, "creator_pct") / 10.0) * d["creator_max"]
    s -= (_f(sig, "owner_pct") / 10.0) * d["owner_max"]
    s -= (_f(sig, "top1_pct") / 10.0) * d["top1_max"]
    s -= (_f(sig, "top10_pct") / 40.0) * d["top10_max"]
    holders = _f(sig, "holder_count")
    s -= max(0.0, min(1.0, (100 - holders) / 100.0)) * d["holders_below_100_max"]
    liq = _f(sig, "liquidity_usd")
    s -= max(0.0, min(1.0, (50_000 - liq) / 50_000.0)) * d["liquidity_below_50k_max"]
    age = _f(sig, "age_min", 9999)
    if age < 60:
        s -= ((60 - age) / 35.0) * d["age_below_60m_max"]
    return max(0.0, round(s, 1))


def momentum(sig, w):
    """Kembalikan (skor 0-100, jumlah sinyal momentum yang menyala)."""
    p = w["momentum_points"]
    s, signals = 0.0, 0
    vm = _f(sig, "volume_mcap_ratio", None) if sig.get("volume_mcap_ratio") is not None \
        else (_f(sig, "volume_24h_usd") / _f(sig, "mcap_usd") if _f(sig, "mcap_usd") else 0.0)
    if vm >= 1:
        s += p["volume_mcap_gte_1"]; signals += 1
    bsr = _f(sig, "buy_sell_ratio")
    if bsr >= 1.3:
        s += p["buy_sell_ratio_gte_1_3"]; signals += 1
    if bsr >= 2:
        s += p["buy_sell_ratio_gte_2"]
    if _f(sig, "holder_growth_1h") > 0:
        s += p["holder_growth_positive"]; signals += 1
    if _f(sig, "liquidity_growth") > 0:
        s += p["liquidity_growth_positive"]
    return min(100.0, round(s, 1)), signals


def smart_money(sig, w):
    p = w["smart_money_points"]
    if int(_f(sig, "fresh_cluster")) == 1:
        return 0.0  # cluster fresh menghabisi sub-skor ini
    s = _f(sig, "established_holders") * p["per_established_holder"]
    return min(p["cap"], round(s, 1))


def score_signal(sig, weights=WEIGHTS):
    sw = weights["subweights"]
    k = keamanan(sig, weights)
    m, m_signals = momentum(sig, weights)
    sm = smart_money(sig, weights)
    total = sw["keamanan"] * k + sw["momentum"] * m + sw["smart_money"] * sm
    th = weights["thresholds"]
    if int(_f(sig, "fresh_cluster")) == 1:
        verdict = "BATAL (fresh cluster)"
    elif total >= th["tier_a"]:
        verdict = "TIER_A_CANDIDATE (gate tetap wajib lolos)"
    elif total >= th["momentum_min"] and m_signals >= th["momentum_signals_min"]:
        verdict = "MOMENTUM_CANDIDATE (gate tetap wajib lolos)"
    else:
        verdict = "WATCH/REJECT"
    return {"keamanan": k, "momentum": m, "momentum_signals": m_signals,
            "smart_money": sm, "score": round(total, 1), "verdict": verdict}


DEMO = [
    {"symbol": "GOOD", "buy_tax": 1, "sell_tax": 1, "lp_unlocked_pct": 2,
     "creator_pct": 1, "owner_pct": 0, "top1_pct": 3, "top10_pct": 18,
     "holder_count": 240, "liquidity_usd": 85000, "age_min": 180,
     "volume_mcap_ratio": 1.6, "buy_sell_ratio": 1.9, "holder_growth_1h": 12,
     "liquidity_growth": 5, "established_holders": 2, "fresh_cluster": 0},
    {"symbol": "TRAP", "buy_tax": 5, "sell_tax": 5, "lp_unlocked_pct": 18,
     "creator_pct": 9, "owner_pct": 8, "top1_pct": 9, "top10_pct": 38,
     "holder_count": 22, "liquidity_usd": 12000, "age_min": 40,
     "volume_mcap_ratio": 3.2, "buy_sell_ratio": 2.6, "holder_growth_1h": 40,
     "liquidity_growth": 30, "established_holders": 0, "fresh_cluster": 1},
]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--json", help="satu sinyal sebagai string JSON")
    a = ap.parse_args()
    rows = DEMO if a.demo else [json.loads(a.json)] if a.json else []
    if not rows:
        ap.error("pakai --demo atau --json")
    for r in rows:
        print(r.get("symbol", "?"), json.dumps(score_signal(r), indent=1))
