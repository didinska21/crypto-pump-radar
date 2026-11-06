#!/usr/bin/env python3
"""Hitung fitur turunan dari data mentah sinyal (lihat docs/05).

Fungsi murni: dict masuk, dict fitur keluar. Nilai yang tidak bisa
dihitung dikembalikan sebagai None — TIDAK PERNAH 0 palsu
(aturan kualitas data, docs/06).
"""


def volume_mcap_ratio(volume_24h_usd, mcap_usd):
    if not volume_24h_usd or not mcap_usd:
        return None
    return round(volume_24h_usd / mcap_usd, 3)


def buy_sell_ratio(buys, sells):
    if buys is None or not sells:
        return None
    return round(buys / sells, 3)


def growth_pct(awal, akhir):
    """Pertumbuhan % dari snapshot awal ke akhir; None bila tak valid."""
    if not awal or akhir is None:
        return None
    return round((akhir - awal) / awal * 100.0, 2)


def momentum_signal_count(f):
    """Hitung berapa dari 4 sinyal Jalur Momentum yang menyala."""
    n = 0
    if (f.get("holder_growth_1h") or 0) > 0:
        n += 1
    if (f.get("volume_mcap_ratio") or 0) >= 1:
        n += 1
    if (f.get("buy_sell_ratio") or 0) > 1:
        n += 1
    if (f.get("established_holders") or 0) >= 1 and not f.get("fresh_cluster"):
        n += 1
    return n


def enrich(raw, prev_snapshot=None):
    """Gabung data mentah + snapshot sebelumnya -> fitur lengkap."""
    f = dict(raw)
    f["volume_mcap_ratio"] = volume_mcap_ratio(
        raw.get("volume_24h_usd"), raw.get("mcap_usd"))
    f["buy_sell_ratio"] = buy_sell_ratio(raw.get("buys_24h"), raw.get("sells_24h"))
    if prev_snapshot:
        f["holder_growth_1h"] = growth_pct(
            prev_snapshot.get("holder_count"), raw.get("holder_count"))
        f["liquidity_growth"] = growth_pct(
            prev_snapshot.get("liquidity_usd"), raw.get("liquidity_usd"))
    f["momentum_signals"] = momentum_signal_count(f)
    return f
