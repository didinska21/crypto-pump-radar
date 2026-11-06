#!/usr/bin/env python3
"""Agen-agen spesialis Crypto Pump Radar (rantai komando multi-agent).

Setiap agen punya SATU keahlian dan TIDAK BISA memerintah agen lain —
semua perintah mengalir lewat Komandan + bus perintah (commander.py).
Matriks wewenang yang mengikat ada di config/agents.json; modul ini
adalah perilaku kerjanya.

  SCOUT     usul kandidat mentah (di live: ingest.py)
  AUDITOR   gate keamanan + VETO mutlak (aturan: docs/03)
  ANALIS    skor komposit (membungkus scoring.py)
  EKSEKUTOR dry-run intent eksekusi — tidak pernah menyentuh jaringan,
            wallet, atau uang. Eksekusi live hidup di mesin operasi.
  PENGAMAT  usul exit mekanis dari harga/likuiditas posisi
  PELAJAR   catat hasil untuk dataset belajar (di live: learn.py)
  PELAPOR   susun baris laporan dari fakta tercatat

Prinsip yang sama di semua agen: tidak mengarang angka, dan ragu = batal.
"""
import scoring

# Ambang gate keras — cermin SOP operasi (docs/03). Satu gagal = veto.
GATE_LIMITS = {
    "max_tax_pct": 10.0,
    "max_lp_unlocked_pct": 20.0,
    "max_creator_pct": 10.0,
    "max_owner_pct": 10.0,
    "max_top1_pct": 10.0,
    "max_top10_pct": 40.0,
    "min_holders": 8,
    "min_liquidity_usd": 10_000.0,
}


def _f(sig, key, default=0.0):
    v = sig.get(key)
    return default if v is None else float(v)


class Scout:
    """Mata: mengajukan kandidat mentah ke Komandan. Tidak menilai."""

    name = "SCOUT"

    def propose(self, signals):
        return [{"symbol": s.get("symbol", "?"), "signal": s} for s in signals]


class Auditor:
    """Penjaga gate. Vonisnya LOLOS atau VETO (+alasan) — dan veto final."""

    name = "AUDITOR"

    def check(self, sig):
        reasons = []
        if int(_f(sig, "honeypot")) == 1:
            reasons.append("honeypot flag=1")
        tax = max(_f(sig, "buy_tax"), _f(sig, "sell_tax"))
        if tax > GATE_LIMITS["max_tax_pct"]:
            reasons.append(f"pajak {tax:g}% > {GATE_LIMITS['max_tax_pct']:g}%")
        if _f(sig, "lp_unlocked_pct") > GATE_LIMITS["max_lp_unlocked_pct"]:
            reasons.append("LP unlocked > 20%")
        if _f(sig, "creator_pct") > GATE_LIMITS["max_creator_pct"]:
            reasons.append("creator% > 10%")
        if _f(sig, "owner_pct") > GATE_LIMITS["max_owner_pct"]:
            reasons.append("owner% > 10%")
        if _f(sig, "top1_pct") > GATE_LIMITS["max_top1_pct"]:
            reasons.append("top1 non-LP > 10%")
        if _f(sig, "top10_pct") > GATE_LIMITS["max_top10_pct"]:
            reasons.append("top10 > 40%")
        if _f(sig, "holder_count") < GATE_LIMITS["min_holders"]:
            reasons.append("holders < 8")
        if _f(sig, "liquidity_usd") < GATE_LIMITS["min_liquidity_usd"]:
            reasons.append("likuiditas < $10.000")
        if int(_f(sig, "fresh_cluster")) == 1:
            reasons.append("cluster wallet fresh/insider tinggi (FRESH_CLUSTER_HIGH)")
        if reasons:
            return {"gate_pass": False, "veto": True, "reasons": reasons}
        return {"gate_pass": True, "veto": False, "reasons": []}


class Analis:
    """Otak skor: membungkus scoring.py. Rekomendasi, bukan perintah."""

    name = "ANALIS"

    def score(self, sig):
        return scoring.score_signal(sig)


class Eksekutor:
    """Tangan — mode DRY-RUN di repo ini.

    Menerima hanya EXECUTE_INTENT yang sudah dinyatakan sah oleh bus
    perintah. Tidak pernah membangun transaksi beneran: yang keluar
    adalah intent tercatat, supaya rantai komando bisa diuji & diaudit
    tanpa menyentuh uang. Adapter live (baw + SOP) hidup di mesin operasi.
    """

    name = "EKSEKUTOR"

    def execute_intent(self, order):
        p = order["payload"]
        return {
            "status": "DRY_RUN_INTENT_ACCEPTED",
            "order_id": order["order_id"],
            "symbol": p.get("symbol"),
            "ca": p.get("ca"),
            "amount_usd": p.get("amount_usd"),
            "note": "dry-run: tidak ada transaksi dibangun/dikirim",
        }


class Pengamat:
    """Pengawas posisi: mengusulkan exit mekanis ke Komandan."""

    name = "PENGAMAT"
    STOP_LOSS = -0.30
    TAKE_PROFIT = 1.00  # +100% dari entry = 2x modal keluar

    def check_position(self, pos, price_now_usd, liquidity_now_usd):
        entry = float(pos["entry_price_usd"])
        chg = (price_now_usd - entry) / entry if entry else 0.0
        liq0 = float(pos.get("liquidity_usd") or 0)
        liq_drop = (liquidity_now_usd - liq0) / liq0 if liq0 else 0.0
        if liq_drop <= -0.50 or chg <= -0.50:
            return {"usul": "EXIT_RUG", "change": round(chg, 4)}
        if chg <= self.STOP_LOSS:
            return {"usul": "EXIT_SL", "change": round(chg, 4)}
        if chg >= self.TAKE_PROFIT:
            return {"usul": "EXIT_TARGET", "change": round(chg, 4)}
        return {"usul": None, "change": round(chg, 4)}


class Pelajar:
    """Memori: mencatat semua hasil — lolos, diveto, ditolak bus."""

    name = "PELAJAR"

    def __init__(self):
        self.records = []

    def record(self, entry):
        self.records.append(entry)
        return {"recorded": len(self.records)}


class Pelapor:
    """Mulut: satu baris laporan per fakta. Tanpa opini tambahan."""

    name = "PELAPOR"

    def line(self, text):
        return f"[LAPORAN] {text}"
