#!/usr/bin/env python3
"""Kumpulkan snapshot harga historis & labeli outcome setiap sinyal.

Tahap LABEL pipeline (docs/06) + Fase 1 roadmap (docs/09): tanpa label,
tidak ada belajar (docs/07). Modul ini yang MENJEMPUT datanya; vonisnya
tetap milik label_outcomes.label() — jangan duplikasi ambang di sini.

Cara kerja:
  - Baca signals.csv (skema data/schema.md; file live operasi BSC Sniper
    kompatibel: timestamp,symbol,ca,pool,age_min,liquidity_usd,score,
    decision,reject_reasons — tanpa kolom harga).
  - Karena signals live tak punya harga deteksi, harga awal diambil dari
    candle OHLCV jam-an GeckoTerminal yang memuat waktu sinyal (close
    candle itu; bila candle pertamanya sesudah sinyal, open candle itu).
  - Per pool cukup SATU panggilan OHLCV (limit 1000 candle jam-an) yang
    mencakup sinyal tertua s/d jendela terjauh yang sudah jatuh tempo.
  - Untuk tiap horizon 1h/6h/24h/7d yang SUDAH jatuh tempo
    (waktu sinyal + horizon <= sekarang) dan belum ada di file label:
    end = close candle terakhir dalam jendela, high/low = ekstrem
    jendela -> pct_change, max_gain_pct, max_drawdown_pct, label.
  - Tak ada candle sama sekali sesudah sinyal = harga praktis hilang
    -> label RUG (note=no_candles_after_signal), pct dikosongkan.
    Likuiditas historis tidak disediakan GeckoTerminal, jadi kriteria
    likuiditas di label() tidak terisi dari jalur ini (liq_end=None).

Keluaran: data/live/labels.csv (data live -> gitignore, tidak masuk repo).
Idempoten: kunci (signal_timestamp, ca, horizon) yang sudah ada dilewati;
jalan ulang hanya mengisi yang kurang.

Pakai:
  python3 label.py                       # semua yang jatuh tempo
  python3 label.py --limit 20            # uji subset dulu
  python3 label.py --signals /path/signals.csv --out data/live/labels.csv
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from label_outcomes import label as verdict  # noqa: E402  (ambang resmi repo)

API = "https://api.geckoterminal.com/api/v2"
HORIZONS = [("1h", 1), ("6h", 6), ("24h", 24), ("7d", 168)]
FIELDS = ["signal_timestamp", "symbol", "ca", "pool", "horizon",
          "price_start_usd", "price_end_usd", "pct_change", "max_gain_pct",
          "max_drawdown_pct", "label", "source", "labeled_at", "note"]
SOURCE = "geckoterminal_ohlcv_hour"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch(url, retries=4):
    """GET JSON; hormati 429 dengan backoff (kuota publik ~30 panggil/mnt)."""
    wait = 5
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < retries:
                time.sleep(wait)
                wait *= 2
                continue
            raise
        except Exception:
            if i == retries:
                raise
            time.sleep(2 * (i + 1))


def pool_candles(pool, before_ts):
    """Candle jam-an [ts, open, high, low, close, volume] menaik per waktu."""
    url = (f"{API}/networks/bsc/pools/{pool}/ohlcv/hour"
           f"?aggregate=1&before_timestamp={before_ts}&limit=1000&currency=usd")
    data = fetch(url)
    lst = (data.get("data", {}).get("attributes", {}) or {}).get("ohlcv_list") or []
    return sorted(lst, key=lambda c: c[0])


def fmt(x):
    return "" if x is None else f"{x:.10g}"


def label_signal(sig, candles, now):
    """Hasilkan baris label untuk semua horizon jatuh tempo dari 1 sinyal."""
    t0 = sig["_t0"]
    rows = []
    # Harga awal: close candle yang memuat t0; fallback candle terakhir
    # sebelum t0; fallback open candle pertama sesudah t0.
    start = None
    prior = [c for c in candles if c[0] <= t0.timestamp()]
    if prior:
        start = prior[-1][4]
    elif candles:
        start = candles[0][1]
    after = [c for c in candles if c[0] + 3600 > t0.timestamp()]
    for name, hours in HORIZONS:
        end_t = t0 + timedelta(hours=hours)
        if end_t > now:
            continue  # belum jatuh tempo
        win = [c for c in after if c[0] < end_t.timestamp()]
        labeled_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        base = {"signal_timestamp": sig["timestamp"], "symbol": sig.get("symbol", ""),
                "ca": sig["ca"], "pool": sig["pool"], "horizon": name,
                "source": SOURCE, "labeled_at": labeled_at}
        if start is None or not win:
            rows.append({**base, "price_start_usd": fmt(start),
                         "price_end_usd": "", "pct_change": "",
                         "max_gain_pct": "", "max_drawdown_pct": "",
                         "label": "RUG", "note": "no_candles_after_signal"})
            continue
        high = max(c[2] for c in win)
        low = min(c[3] for c in win)
        end = win[-1][4]
        stale = (end_t.timestamp() - (win[-1][0] + 3600)) > 3 * 3600
        rows.append({**base,
                     "price_start_usd": fmt(start), "price_end_usd": fmt(end),
                     "pct_change": fmt((end - start) / start * 100),
                     "max_gain_pct": fmt((high - start) / start * 100),
                     "max_drawdown_pct": fmt((low - start) / start * 100),
                     "label": verdict(start, high, end, None, None),
                     "note": "stale_end" if stale else ""})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signals",
                    default=os.path.expanduser("~/workspace/bsc-sniper/state/signals.csv"))
    ap.add_argument("--out", default=os.path.join(REPO, "data/live/labels.csv"))
    ap.add_argument("--limit", type=int, default=0, help="maks sinyal diproses (0=semua)")
    ap.add_argument("--delay", type=float, default=2.1,
                    help="jeda antar panggilan API detik (kuota publik ~30/mnt)")
    a = ap.parse_args()

    with open(a.signals, newline="", encoding="utf-8") as f:
        signals = list(csv.DictReader(f))
    for s in signals:
        s["_t0"] = datetime.fromisoformat(s["timestamp"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    done = set()
    if os.path.exists(a.out):
        with open(a.out, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                done.add((r["signal_timestamp"], r["ca"], r["horizon"]))

    # Hanya sinyal yang punya >=1 horizon jatuh tempo & belum lengkap.
    todo = []
    for s in signals:
        due = [n for n, h in HORIZONS if s["_t0"] + timedelta(hours=h) <= now]
        if due and any((s["timestamp"], s["ca"], n) not in done for n in due):
            todo.append(s)
    todo.sort(key=lambda s: s["_t0"])
    if a.limit:
        todo = todo[:a.limit]

    # Kelompokkan per pool: 1 panggilan untuk jendela terjauh yang dibutuhkan.
    by_pool = {}
    for s in todo:
        by_pool.setdefault(s["pool"], []).append(s)

    new_rows, errors = [], []
    for i, (pool, sigs) in enumerate(by_pool.items(), 1):
        before = int(min(now, max(s["_t0"] for s in sigs)
                         + timedelta(hours=168)).timestamp()) + 3600
        try:
            candles = pool_candles(pool, before)
        except Exception as e:  # API gagal utk pool ini -> catat, lanjut
            errors.append(f"{pool}: {type(e).__name__} {e}")
            continue
        for s in sigs:
            for r in label_signal(s, candles, now):
                if (r["signal_timestamp"], r["ca"], r["horizon"]) not in done:
                    new_rows.append(r)
        if i < len(by_pool):
            time.sleep(a.delay)

    if new_rows:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        fresh = not os.path.exists(a.out)
        with open(a.out, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if fresh:
                w.writeheader()
            w.writerows(new_rows)

    from collections import Counter
    per_h = Counter(r["horizon"] for r in new_rows)
    per_l = Counter(r["label"] for r in new_rows)
    print(f"Sinyal diproses: {len(todo)} dari {len(by_pool)} pool unik "
          f"(total sinyal di file: {len(signals)})")
    print(f"Baris label baru: {len(new_rows)} -> {a.out}")
    print("Per horizon:", dict(sorted(per_h.items())))
    print("Distribusi label:", dict(per_l.most_common()))
    print(f"Error API: {len(errors)}")
    for e in errors[:10]:
        print("  !", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
