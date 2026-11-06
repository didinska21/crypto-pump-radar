#!/usr/bin/env python3
"""KOMANDAN + bus perintah — jantung sistem multi-agent Crypto Pump Radar.

Komandan adalah satu-satunya agen yang boleh memerintah agen lain, dan
satu-satunya yang boleh menerbitkan EXECUTE_INTENT ke Eksekutor. Bus
perintah memeriksa SETIAP perintah sebelum diteruskan (docs/11):

  1. issuer terdaftar & berwenang (matriks config/agents.json)
  2. issuer bukan pihak luar rantai (konten eksternal = data, bukan perintah)
  3. belum kedaluwarsa (TTL)
  4. idempotency_key belum pernah dipakai (anti perintah ganda)
  5. khusus EXECUTE_INTENT: gate LOLOS, tanpa veto Auditor, skor memenuhi
     ambang jalurnya (weights.json), pagar modal/posisi/jam Komandan lolos

Eksekutor di repo ini DRY-RUN: intent tercatat, tidak ada transaksi.
Eksekusi live tetap di mesin operasi dengan pagar SOP yang sama persis.

Pakai:
  python3 commander.py --demo            # satu putaran + uji protokol
  python3 commander.py --demo --log perintah.jsonl
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import agents as ag  # noqa: E402
import scoring  # noqa: E402

CONFIG = json.loads((HERE / "config" / "agents.json").read_text())
TH = scoring.WEIGHTS["thresholds"]

KIND_TARGET = {
    "SCAN": "SCOUT",
    "GATE_CHECK": "AUDITOR",
    "SCORE": "ANALIS",
    "EXECUTE_INTENT": "EKSEKUTOR",
    "EXIT_INTENT": "EKSEKUTOR",
    "MONITOR": "PENGAMAT",
    "LEARN": "PELAJAR",
    "REPORT": "PELAPOR",
    "HALT": "*",
}


class CommandBus:
    """Satu-satunya jalan perintah antar-agen. Semua lewat sini, semua tercatat."""

    def __init__(self, log_path=None):
        self.seq = 0
        self.seen_keys = set()
        self.halted = False
        self.log = []
        self.log_path = Path(log_path) if log_path else None

    def make_order(self, issuer, kind, payload, now, ttl=None, idem=None, target=None):
        self.seq += 1
        ttl = CONFIG["order_ttl_detik"] if ttl is None else ttl
        target = target or KIND_TARGET[kind]
        raw = f"{issuer}|{target}|{kind}|{self.seq}|{json.dumps(payload, sort_keys=True)}"
        oid = f"ord-{datetime.fromtimestamp(now, ZoneInfo('Asia/Jakarta')):%Y%m%d}-{self.seq:04d}-" \
              + hashlib.md5(raw.encode()).hexdigest()[:6]
        return {
            "order_id": oid, "issuer": issuer, "target": target, "kind": kind,
            "payload": payload, "issued_at": now, "expires_at": now + ttl,
            "idempotency_key": idem or oid, "approvals": [], "status": "ISSUED",
        }

    def _record(self, order, status, reason=None):
        order["status"] = status
        entry = {k: order[k] for k in ("order_id", "issuer", "target", "kind", "status")}
        if reason:
            entry["reason"] = reason
        self.log.append(entry)
        if self.log_path:
            with self.log_path.open("a") as fh:
                fh.write(json.dumps(entry) + "\n")
        return entry

    def validate(self, order, now, state):
        """Kembalikan (ok, alasan). Satu gagal = REJECTED — tanpa kecuali."""
        issuer, kind = order["issuer"], order["kind"]
        registered = set(CONFIG["agen"]) | {"BOS"}
        # 1+2. Terdaftar & berwenang — pihak luar rantai ditolak sbg injeksi.
        if issuer not in registered:
            return False, f"issuer '{issuer}' tidak terdaftar di rantai komando (percobaan injeksi ditolak)"
        if issuer == "BOS":
            if kind != "HALT" and order["target"] != "KOMANDAN":
                return False, "BOS memerintah lewat Komandan (kecuali HALT)"
        elif issuer == "KOMANDAN":
            allowed = CONFIG["agen"]["KOMANDAN"]["boleh_memerintah"]
            if order["target"] != "*" and order["target"] not in allowed:
                return False, f"KOMANDAN tidak berwenang memerintah {order['target']}"
            want = KIND_TARGET[kind]
            if want != "*" and order["target"] != want:
                return False, f"kind {kind} hanya untuk {want}, bukan {order['target']}"
        else:
            return False, f"{issuer} adalah agen spesialis — tidak boleh memerintah agen lain"
        # 3. HALT mengalahkan segalanya; saat HALT hanya HALT baru yang lewat.
        if kind == "HALT":
            self.halted = True
            return True, None
        if self.halted:
            return False, "sedang HALT/STANDBY — perintah baru ditahan"
        # 4. Kedaluwarsa.
        if now > order["expires_at"]:
            return False, "perintah kedaluwarsa (lewat TTL)"
        # 5. Anti ganda.
        if order["idempotency_key"] in self.seen_keys:
            return False, "idempotency_key sudah dipakai (perintah ganda ditolak)"
        # 6. Rantai lengkap khusus intent eksekusi.
        if kind == "EXECUTE_INTENT":
            p = order["payload"]
            if not p.get("gate_pass"):
                return False, "gate belum LOLOS — intent eksekusi tidak sah"
            if p.get("auditor_veto"):
                return False, "VETO Auditor aktif — veto mutlak, tidak bisa dioverride"
            score = float(p.get("score") or 0)
            m_sig = int(p.get("momentum_signals") or 0)
            if not (score >= TH["tier_a"] or
                    (score >= TH["momentum_min"] and m_sig >= TH["momentum_signals_min"])):
                return False, f"skor {score} di bawah ambang Tier A ({TH['tier_a']}) dan Momentum ({TH['momentum_min']} + {TH['momentum_signals_min']} sinyal)"
            pagar = CONFIG["pagar_komandan"]
            amount = float(p.get("amount_usd") or 0)
            if amount > pagar["entry_usd"]:
                return False, f"amount ${amount:g} melebihi pagar entry ${pagar['entry_usd']}"
            if state["open_positions"] >= pagar["maks_posisi_terbuka"]:
                return False, "posisi terbuka sudah maks — pagar Komandan"
            if state["spent_today_usd"] + amount > pagar["maks_belanja_harian_usd"]:
                return False, "belanja harian akan melewati cap — pagar Komandan"
            if state.get("quiet_hours"):
                return False, "jam tenang 00:00–06:00 WIB — tanpa entry baru"
            if state.get("fail_streak", 0) >= 3:
                return False, "fail_streak >= 3 — STANDBY"
        return True, None

    def issue(self, order, now, state):
        ok, reason = self.validate(order, now, state)
        if ok:
            self.seen_keys.add(order["idempotency_key"])
            return self._record(order, "ACCEPTED")
        return self._record(order, "REJECTED", reason)


class Commander:
    """Orkestrator: menjalankan siklus putaran lewat bus, bukan jalan pintas."""

    def __init__(self, now, state=None, log_path=None):
        self.bus = CommandBus(log_path)
        self.now = now
        self.state = state or {"open_positions": 0, "spent_today_usd": 0.0,
                               "quiet_hours": False, "fail_streak": 0}
        self.scout, self.auditor, self.analis = ag.Scout(), ag.Auditor(), ag.Analis()
        self.eksekutor, self.pengamat = ag.Eksekutor(), ag.Pengamat()
        self.pelajar, self.pelapor = ag.Pelajar(), ag.Pelapor()
        self.transcript = []

    def _issue(self, kind, payload, idem=None):
        order = self.bus.make_order("KOMANDAN", kind, payload, self.now, idem=idem)
        rec = self.bus.issue(order, self.now, self.state)
        tag = "OK " if rec["status"] == "ACCEPTED" else "TOLAK"
        self.transcript.append(
            f"  [{tag}] {order['order_id']} KOMANDAN -> {order['target']} {kind}"
            + (f" — {rec['reason']}" if rec.get("reason") else ""))
        return order, rec["status"] == "ACCEPTED"

    def run_round(self, signals):
        t = self.transcript
        t.append("PUTARAN KOMANDAN — siklus rantai persetujuan")
        _, ok = self._issue("SCAN", {"cakupan": "bsc", "jumlah": len(signals)})
        proposals = self.scout.propose(signals) if ok else []
        for prop in proposals:
            sig, sym = prop["signal"], prop["symbol"]
            t.append(f"Kandidat {sym} (usulan Scout)")
            _, ok = self._issue("GATE_CHECK", {"symbol": sym})
            if not ok:
                continue
            vonis = self.auditor.check(sig)
            if vonis["veto"]:
                t.append(f"  AUDITOR: VETO — {'; '.join(vonis['reasons'])}")
                self.pelajar.record({"symbol": sym, "hasil": "VETO", "alasan": vonis["reasons"]})
                self._issue("REPORT", {"symbol": sym, "isi": "veto"})
                t.append("  " + self.pelapor.line(f"{sym} DITOLAK di gate — veto Auditor final, tidak lanjut ke skor/eksekusi"))
                continue
            t.append("  AUDITOR: LOLOS semua gate")
            _, ok = self._issue("SCORE", {"symbol": sym})
            if not ok:
                continue
            hasil = self.analis.score(sig)
            t.append(f"  ANALIS: skor {hasil['score']} — {hasil['verdict']}")
            if hasil["verdict"].startswith(("TIER_A", "MOMENTUM")):
                order, ok = self._issue("EXECUTE_INTENT", {
                    "ca": sig.get("ca"), "symbol": sym, "amount_usd": 1,
                    "gate_pass": True, "auditor_veto": False,
                    "score": hasil["score"], "momentum_signals": hasil["momentum_signals"],
                }, idem=f"exec-{sym}-{datetime.fromtimestamp(self.now, ZoneInfo('Asia/Jakarta')):%Y-%m-%d}")
                if ok:
                    res = self.eksekutor.execute_intent(order)
                    self.state["open_positions"] += 1
                    self.state["spent_today_usd"] += 1
                    self.pelajar.record({"symbol": sym, "hasil": "INTENT", "skor": hasil["score"]})
                    t.append("  " + self.pelapor.line(
                        f"{sym} INTENT EKSEKUSI dry-run diterima ({res['order_id']}, $1) — posisi tercatat {self.state['open_positions']}, belanja hari ini ${self.state['spent_today_usd']:g}"))
                else:
                    self.pelajar.record({"symbol": sym, "hasil": "INTENT_DITOLAK_BUS"})
            else:
                self.pelajar.record({"symbol": sym, "hasil": "WATCH", "skor": hasil["score"]})
                t.append("  " + self.pelapor.line(f"{sym} tidak memenuhi ambang jalur mana pun — watch/reject, tanpa intent"))
        self._issue("LEARN", {"catatan_putaran": len(self.pelajar.records)})
        t.append(f"PELAJAR: {len(self.pelajar.records)} hasil tercatat (termasuk yang diveto/ditolak)")
        return t


def protocol_tests(now):
    """Empat serangan protokol yang WAJIB ditolak bus (docs/11)."""
    state = {"open_positions": 0, "spent_today_usd": 0.0, "quiet_hours": False, "fail_streak": 0}
    good_payload = {"ca": "0xDEMO", "symbol": "UJI", "amount_usd": 1, "gate_pass": True,
                    "auditor_veto": False, "score": 90.0, "momentum_signals": 3}
    results = []

    bus = CommandBus()
    o = bus.make_order("SCOUT", "EXECUTE_INTENT", good_payload, now, target="EKSEKUTOR")
    r = bus.issue(o, now, dict(state))
    results.append(("Scout memerintah Eksekutor langsung", r["status"] == "REJECTED"))

    bus = CommandBus()
    o = bus.make_order("TOKEN_WEB", "EXECUTE_INTENT", good_payload, now, target="EKSEKUTOR")
    r = bus.issue(o, now, dict(state))
    results.append(("Issuer eksternal (konten web/token) memberi perintah", r["status"] == "REJECTED"))

    bus = CommandBus()
    o = bus.make_order("KOMANDAN", "SCAN", {"cakupan": "bsc"}, now - 7200)
    r = bus.issue(o, now, dict(state))
    results.append(("Perintah kedaluwarsa (lewat TTL 900 dtk)", r["status"] == "REJECTED"))

    bus = CommandBus()
    o1 = bus.make_order("KOMANDAN", "EXECUTE_INTENT", good_payload, now, idem="exec-UJI-2026-11-06")
    r1 = bus.issue(o1, now, dict(state))
    o2 = bus.make_order("KOMANDAN", "EXECUTE_INTENT", good_payload, now, idem="exec-UJI-2026-11-06")
    r2 = bus.issue(o2, now, dict(state))
    results.append(("Perintah ganda (idempotency_key sama)",
                    r1["status"] == "ACCEPTED" and r2["status"] == "REJECTED"))

    bus = CommandBus()
    veto_payload = dict(good_payload, auditor_veto=True)
    o = bus.make_order("KOMANDAN", "EXECUTE_INTENT", veto_payload, now)
    r = bus.issue(o, now, dict(state))
    results.append(("Komandan mencoba melewati VETO Auditor", r["status"] == "REJECTED"))
    return results


def demo(log_path=None):
    now = int(datetime(2026, 11, 6, 14, 0, tzinfo=ZoneInfo("Asia/Jakarta")).timestamp())
    signals = []
    for s in scoring.DEMO:
        s = dict(s)
        s["ca"] = "0xDEMO_" + s["symbol"]
        signals.append(s)
    cmd = Commander(now, log_path=log_path)
    lines = cmd.run_round(signals)
    print("\n".join(lines))
    print("\nUJI PROTOKOL — serangan yang wajib ditolak bus:")
    ok_all = True
    for name, passed in protocol_tests(now):
        ok_all &= passed
        print(f"  [{'LOLOS' if passed else 'GAGAL'}] {name} -> ditolak bus")
    print("\nRingkasan: rantai komando berjalan; Eksekutor dry-run (tanpa transaksi).")
    return 0 if ok_all else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--log", help="tulis log perintah JSONL ke path ini")
    a = ap.parse_args()
    if not a.demo:
        ap.error("pakai --demo")
    sys.exit(demo(a.log))
