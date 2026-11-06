#!/usr/bin/env python3
"""MODE SHADOW — putar ulang sinyal produksi lewat rantai Komandan.

Shadow memutar ULANG baris-baris yang sudah tercatat di signals.csv operasi
live (bsc-sniper) lewat rantai komando repo ini — Scout usul → Auditor
gate/veto → Analis skor → Komandan cek pagar bus → Eksekutor dry-run —
lalu membandingkan vonis rantai dengan keputusan produksi yang tercatat.
Shadow READ-ONLY total: tidak membaca state live selain signals.csv,
tidak menulis apa pun ke operasi, tidak mengambil keputusan live.

KENYATAAN DATA (jangan disembunyikan): signals.csv produksi hanya menyimpan
kolom ringkas + `reject_reasons`. Nilai fitur yang GAGAL gate tercatat di
dalam alasan (mis. "lp_unlocked>20% (100.0%)") dan bisa dipulihkan persis;
fitur yang LOLOS gate tidak menyimpan nilainya; fitur momentum & smart
money TIDAK PERNAH disimpan. Maka shadow bekerja dalam tiga lapisan:

  L1 AUDITOR REPO   — veto dari agents.Auditor atas nilai yang benar-benar
                      terpulihkan. Alasan veto yang lahir dari fitur MISSING
                      (artefak default modul, mis. holder_count tak terisi
                      terbaca 0 -> "holders < 8") DIBUANG dan dicatat
                      sebagai artefak — produksi membuktikan fitur itu
                      lolos, jadi veto seperti itu karangan data, bukan vonis.
  L2 CATATAN PRODUKSI — kegagalan gate yang tercatat produksi tapi di luar
                      model Auditor repo (docs/03 SOP produksi lebih luas):
                      not_open_source, mintable, proxy, blacklisted,
                      pausable_or_takeback, dan kegagalan bernilai None
                      (fakta gagalnya tercatat, nilainya tidak).
  L3 DATA TAK TERVERIFIKASI — sumber gate tidak memberi data (goplus_no_data,
                      honeypot_is_fetch_fail, honeypot_is_sim_fail).
                      Sesuai pagar "ragu = batal", lapisan ini memblokir.

Skor Analis dihitung dari fitur parsial dan DILABELI begitu: sub-skor
momentum/smart-money selalu 0 di dataset ini karena fiturnya tidak pernah
tersimpan, jadi skor bayangan TIDAK sebanding dengan skor produksi v1.

Pakai:
  python3 shadow.py                      # semua baris signals.csv live
  python3 shadow.py --limit 100          # 100 baris terakhir
  python3 shadow.py --csv X --out Y      # sumber/keluaran lain

Keluaran: data/live/shadow_log.jsonl (gitignored) + ringkasan ke stdout.
"""
import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import commander as cm  # noqa: E402

WIB = ZoneInfo("Asia/Jakarta")
DEFAULT_CSV = Path.home() / "workspace" / "bsc-sniper" / "state" / "signals.csv"
DEFAULT_OUT = HERE.parent / "data" / "live" / "shadow_log.jsonl"

# Fitur yang diminta rantai Komandan (Auditor + scoring.py).
FEATURES = ["honeypot", "buy_tax", "sell_tax", "lp_unlocked_pct",
            "creator_pct", "owner_pct", "top1_pct", "top10_pct",
            "holder_count", "liquidity_usd", "age_min",
            "volume_mcap_ratio", "buy_sell_ratio", "holder_growth_1h",
            "liquidity_growth", "established_holders", "fresh_cluster"]

# Token reject_reasons -> fitur commander (kegagalan berambang dengan nilai).
NUMERIC_FAIL = {
    "buy_tax>10%": "buy_tax", "sell_tax>10%": "sell_tax",
    "lp_unlocked>20%": "lp_unlocked_pct", "creator_pct>10%": "creator_pct",
    "owner_pct>10%": "owner_pct", "top1_holder>10%": "top1_pct",
    "top10_holders>40%": "top10_pct", "holders<8": "holder_count",
}
# Kegagalan kontrak yang tercatat produksi, di luar model Auditor repo.
PROD_GATE_FAIL = {"not_open_source", "mintable", "proxy", "blacklisted",
                  "pausable_or_takeback"}
# Sumber data gate tidak memberi jawaban -> ragu = batal.
DATA_GAPS = {"goplus_no_data": "GoPlus tanpa data",
             "honeypot_is_fetch_fail": "honeypot.is gagal diambil",
             "honeypot_is_sim_fail": "simulasi honeypot.is gagal"}
HONEYPOT_FAIL = {"honeypot_goplus", "honeypot_is_flag"}


def _num(raw):
    """'(100.0%)' / '(0)' -> float; '(None)' -> None (gagal, nilai tak tercatat)."""
    if raw is None or raw == "None":
        return None
    return float(raw.rstrip("%"))


def parse_signal(row):
    """Satu baris signals.csv -> (kandidat fitur, buku status fitur, lapisan).

    Hanya nilai yang benar-benar tercatat yang masuk kandidat. Status tiap
    fitur dicatat apa adanya: langsung / terpulihkan / lolos_tak_ternilai /
    gagal_tanpa_nilai / tidak_terverifikasi / missing.
    """
    sig = {"symbol": row["symbol"], "ca": row["ca"],
           "age_min": int(row["age_min"]),
           "liquidity_usd": float(row["liquidity_usd"])}
    status = {"age_min": "langsung", "liquidity_usd": "langsung"}
    prod_fails, data_gaps, notes = [], [], []
    failed_feats = set()

    for part in row["reject_reasons"].split(";"):
        part = part.strip()
        if not part:
            continue
        if part.startswith("recheck: "):
            part = part[len("recheck: "):]
        m = re.match(r"^([a-z0-9_<>%]+)(?:\s*\(([^)]*)\))?$", part)
        token, raw_val = (m.group(1), m.group(2)) if m else (part, None)
        if token in NUMERIC_FAIL:
            feat = NUMERIC_FAIL[token]
            failed_feats.add(feat)
            val = _num(raw_val)
            if val is not None:
                sig[feat] = val
                status[feat] = "terpulihkan"
            else:
                status[feat] = "gagal_tanpa_nilai"
                prod_fails.append(f"{token} (nilai tidak tercatat)")
        elif token in HONEYPOT_FAIL:
            sig["honeypot"] = 1
            status["honeypot"] = "terpulihkan"
            failed_feats.add("honeypot")
        elif token in PROD_GATE_FAIL:
            prod_fails.append(token)
        elif token in DATA_GAPS:
            data_gaps.append(DATA_GAPS[token])
        elif token == "honeypot_is_pair_not_found":
            notes.append("honeypot.is: pair tidak terindeks (cakupan sumber "
                         "kedua hilang; GoPlus tetap sumber primer)")
        else:
            notes.append(f"alasan produksi tak terpetakan: {part}")

    # Fitur berambang yang TIDAK ditandai gagal = lolos menurut catatan
    # produksi, tapi nilai pastinya tidak pernah disimpan.
    for feat in ("buy_tax", "sell_tax", "lp_unlocked_pct", "creator_pct",
                 "owner_pct", "top1_pct", "top10_pct", "holder_count"):
        if feat not in status:
            status[feat] = "lolos_tak_ternilai"
    if "honeypot" not in status:
        status["honeypot"] = ("tidak_terverifikasi" if data_gaps
                              else "tersirat_lolos_goplus")
    for feat in FEATURES:
        status.setdefault(feat, "missing")
    return sig, status, prod_fails, data_gaps, notes


def run_chain(sig, ts_epoch):
    """Jalankan rantai Komandan (dry-run) untuk SATU kandidat.

    Komandan + bus + agen semuanya modul repo; yang ditambah shadow hanya
    rekonsiliasi artefak missing pada vonis Auditor (lihat docstring).
    """
    hour_wib = datetime.fromtimestamp(ts_epoch, WIB).hour
    cmd = cm.Commander(ts_epoch, state={
        "open_positions": 0, "spent_today_usd": 0.0,
        "quiet_hours": hour_wib < 6, "fail_streak": 0})
    cmd._issue("SCAN", {"cakupan": "shadow-replay", "jumlah": 1})
    prop = cmd.scout.propose([sig])[0]

    cmd._issue("GATE_CHECK", {"symbol": prop["symbol"]})
    vonis = cmd.auditor.check(sig)
    reasons, artefak = [], []
    for r in vonis["reasons"]:
        # "holders < 8" tanpa nilai holder_count terpulihkan = artefak
        # default 0 pada fitur missing; catatan produksi membuktikan lolos.
        if r == "holders < 8" and "holder_count" not in sig:
            artefak.append(r)
        else:
            reasons.append(r)
    gate_pass = not reasons

    hasil = {"auditor": {"veto": not gate_pass, "reasons": reasons,
                         "artefak_missing_dibuang": artefak},
             "analis": None, "intent": None}
    if not gate_pass:
        return hasil

    cmd._issue("SCORE", {"symbol": prop["symbol"]})
    skor = cmd.analis.score(sig)
    hasil["analis"] = skor
    if skor["verdict"].startswith(("TIER_A", "MOMENTUM")):
        order, ok = cmd._issue("EXECUTE_INTENT", {
            "ca": sig.get("ca"), "symbol": prop["symbol"], "amount_usd": 1,
            "gate_pass": True, "auditor_veto": False,
            "score": skor["score"],
            "momentum_signals": skor["momentum_signals"],
        }, idem=f"shadow-{sig.get('ca')}-{prop['symbol']}")
        hasil["intent"] = {"diterbitkan": True, "bus_diterima": ok,
                           "eksekutor": (cmd.eksekutor.execute_intent(order)
                                         if ok else None)}
    return hasil


def shadow_verdict(chain, prod_fails, data_gaps):
    """Vonis akhir shadow: lapisan pemblokir pertama yang terbukti."""
    if chain["auditor"]["veto"]:
        return "VETO_AUDITOR"
    if prod_fails:
        return "VETO_PRODUKSI"
    if data_gaps:
        return "VETO_DATA"
    if chain["intent"] and chain["intent"]["bus_diterima"]:
        return "INTENT"
    if chain["intent"]:
        return "INTENT_DITOLAK_PAGAR"
    return "LOLOS_TANPA_INTENT"


def main():
    ap = argparse.ArgumentParser(description="Mode shadow: putar ulang "
                                             "signals.csv lewat rantai Komandan")
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--limit", type=int, help="hanya N baris terakhir")
    a = ap.parse_args()

    rows = list(csv.DictReader(Path(a.csv).open()))
    if a.limit:
        rows = rows[-a.limit:]
    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    for row in rows:
        sig, status, prod_fails, data_gaps, notes = parse_signal(row)
        ts = int(datetime.fromisoformat(row["timestamp"]).timestamp())
        chain = run_chain(sig, ts)
        verdict = shadow_verdict(chain, prod_fails, data_gaps)
        pasti = [f for f in FEATURES if status[f] in ("langsung", "terpulihkan")]
        rec = {
            "timestamp": row["timestamp"], "symbol": row["symbol"],
            "ca": row["ca"], "pool": row["pool"],
            "fitur": {
                "nilai_pasti": pasti,
                "lolos_tak_ternilai": [f for f in FEATURES
                                       if status[f] == "lolos_tak_ternilai"],
                "gagal_tanpa_nilai": [f for f in FEATURES
                                      if status[f] == "gagal_tanpa_nilai"],
                "tidak_terverifikasi": [f for f in FEATURES
                                        if status[f] == "tidak_terverifikasi"],
                "missing": [f for f in FEATURES if status[f] == "missing"],
                "kelengkapan_pct": round(100 * len(pasti) / len(FEATURES), 1),
            },
            "auditor": chain["auditor"],
            "lapisan_produksi": {"gagal_tercatat": prod_fails},
            "data_tak_terverifikasi": data_gaps,
            "catatan": notes,
            "analis": (dict(chain["analis"],
                            catatan="skor fitur parsial — momentum & "
                                    "smart-money selalu 0 di dataset ini")
                       if chain["analis"] else None),
            "intent": chain["intent"],
            "produksi": {"decision": row["decision"],
                         "score": float(row["score"]),
                         "reject_reasons": row["reject_reasons"]},
            "shadow_verdict": verdict,
            "sepakat": verdict != "INTENT",
        }
        records.append(rec)

    with out_path.open("w") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ---------- ringkasan ----------
    n = len(records)
    sepakat = sum(r["sepakat"] for r in records)
    from collections import Counter
    by_verdict = Counter(r["shadow_verdict"] for r in records)
    kel = [r["fitur"]["kelengkapan_pct"] for r in records]
    print(f"MODE SHADOW — putar ulang {n} sinyal produksi ({a.csv})")
    print(f"Log: {out_path}")
    print(f"Kelengkapan fitur per sinyal: rata-rata {sum(kel)/n:.1f}% "
          f"dari {len(FEATURES)} fitur rantai (nilai pasti saja)")
    print(f"Vonis: " + ", ".join(f"{k}={v}" for k, v in by_verdict.most_common()))
    print(f"Veto Auditor (L1, nilai terpulihkan): {by_verdict.get('VETO_AUDITOR', 0)}")
    print(f"Sepakat dengan produksi: {sepakat}/{n} ({100*sepakat/n:.1f}%)")
    print("  (produksi di file ini 100% REJECT — kelompok 'shadow tolak, "
          "produksi lolos' tidak terukur dari file ini)")
    beda = [r for r in records if not r["sepakat"]]
    print(f"Perbedaan — shadow INTENT tapi produksi REJECT: {len(beda)}")
    for r in beda[:3]:
        print(f"  - {r['symbol']} {r['ca']} skor analis {r['analis']['score']} "
              f"vs produksi {r['produksi']['score']}; alasan produksi: "
              f"{r['produksi']['reject_reasons']}")
    lolos = [r for r in records if r["shadow_verdict"] == "LOLOS_TANPA_INTENT"]
    print(f"Gate lolos semua lapisan tapi skor di bawah ambang "
          f"(LOLOS_TANPA_INTENT): {len(lolos)}")
    for r in lolos[:3]:
        print(f"  - {r['symbol']} {r['ca']} skor analis "
              f"{r['analis']['score']} (ambang Tier A 80 tak terjangkau: "
              f"momentum+smart-money missing) vs produksi "
              f"{r['produksi']['score']}; alasan produksi: "
              f"{r['produksi']['reject_reasons']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
