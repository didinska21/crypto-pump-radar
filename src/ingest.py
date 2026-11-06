#!/usr/bin/env python3
"""Ingest pool baru dari GeckoTerminal (tanpa API key).

Tahap INGEST pipeline (docs/06). Menghasilkan baris mentah siap ENRICH:
ca, pool, umur, harga, likuiditas, volume. Keputusan/gate TIDAK di sini —
itu pekerjaan screener operasi (bsc-sniper) dan scoring.py.

Pakai:
  python3 ingest.py --network bsc --pages 1
"""
import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone

API = "https://api.geckoterminal.com/api/v2"
QUOTES = {"WBNB", "BNB", "USDT", "USDC", "BUSD", "WETH", "BTCB", "ETH"}


def fetch(url, retries=2):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())
        except Exception:
            if i == retries:
                raise
            time.sleep(2 * (i + 1))


def new_pools(network="bsc", pages=1):
    out, seen = [], set()
    for p in range(1, pages + 1):
        data = fetch(f"{API}/networks/{network}/new_pools?page={p}")
        for pool in data.get("data", []):
            at = pool["attributes"]
            toks = (pool.get("relationships", {}))
            base = at.get("name", "").split("/")[0].strip()
            ca = (toks.get("base_token", {}).get("data", {}) or {}).get("id", "")
            ca = ca.split("_")[-1] if ca else ""
            if not ca or ca in seen or base in QUOTES:
                continue
            seen.add(ca)
            created = at.get("pool_created_at")
            age = None
            if created:
                t = datetime.fromisoformat(created.replace("Z", "+00:00"))
                age = (datetime.now(timezone.utc) - t).total_seconds() / 60
            out.append({
                "symbol": base, "ca": ca, "pool": at.get("address"),
                "chain": network, "age_min": round(age) if age else None,
                "price_usd": at.get("base_token_price_usd"),
                "liquidity_usd": at.get("reserve_in_usd"),
                "volume_24h_usd": (at.get("volume_usd") or {}).get("h24"),
            })
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--network", default="bsc")
    ap.add_argument("--pages", type=int, default=1)
    a = ap.parse_args()
    for row in new_pools(a.network, a.pages):
        print(json.dumps(row))
