"""Generate a synthetic copy of the IPHO operational databases.

Mirrors the real Supabase schemas of the IPHO Medicine Inventory app (`public`)
and the Outpatient Clinic app (`clinic`) column-for-column, so the same
ingestion and dbt code runs against the real systems later. Only analytical
tables are generated; auth/session tables (users, login_log) are not.

Realism baked in on purpose, because it is what the pipeline has to handle:
  * monthly seasonality per therapeutic class + a mild upward trend
  * FEFO (first-expiry-first-out) batch picking and periodic restocks
  * inventory dates stored as TEXT, with a share in the legacy Google-Sheets
    format (MM/DD/YYYY) from before the 2025 migration to Supabase
  * free-text clinic diagnoses with spelling variants
  * a handful of deliberately bad rows (blank expiry, zero-qty lines)

Usage:  python -m ipho_synth.generate --out data/source --seed 42
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from ipho_synth import reference as ref

START = date(2024, 1, 1)
END = date(2026, 9, 30)
SHEETS_MIGRATION = date(2025, 3, 1)  # rows before this mostly carry legacy date strings
PHT = timezone(timedelta(hours=8))


def _legacy_or_iso(d: date, rng: random.Random) -> str:
    if d < SHEETS_MIGRATION and rng.random() < 0.6:
        return d.strftime("%m/%d/%Y")
    return d.isoformat()


def _ts(d: date, rng: random.Random) -> str:
    t = datetime(d.year, d.month, d.day, rng.randint(8, 16), rng.randint(0, 59), tzinfo=PHT)
    return t.isoformat()


def _trend(d: date) -> float:
    """~6% yearly growth in demand."""
    return 1.0 + 0.06 * ((d - START).days / 365.0)


@dataclass
class Batch:
    batch_id: str
    medicine_id: str
    store_room: str
    lot_number: str
    expiry: date | None
    beginning_qty: int
    source_of_fund: str
    received: date
    remaining: int = field(init=False)

    def __post_init__(self) -> None:
        self.remaining = self.beginning_qty


@dataclass
class Tables:
    rows: dict[str, list[dict]] = field(default_factory=dict)

    def add(self, table: str, row: dict) -> None:
        self.rows.setdefault(table, []).append(row)


class InventoryGenerator:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.t = Tables()
        self.batches: dict[str, list[Batch]] = {}
        self.meds = {f"MED-{code}": m for code, *m in ref.MEDICINES}
        self._batch_seq = 0
        self._event_seq = 0
        self._dist_seq = 0
        self._restock_seq = 0
        self._return_seq = 0

    # ── batches & restocks ──────────────────────────────────────────────
    def _new_batch(self, med_id: str, qty: int, received: date) -> Batch:
        self._batch_seq += 1
        expiry: date | None = received + timedelta(days=self.rng.randint(300, 1100))
        if self.rng.random() < 0.01:
            expiry = None  # bad row: expiry never encoded
        b = Batch(
            batch_id=f"BAT-{self._batch_seq:05d}",
            medicine_id=med_id,
            store_room=self.rng.choice(ref.STORE_ROOMS),
            lot_number=f"L{self.rng.randint(10, 99)}{self.rng.choice('ABCDEFGHJK')}"
                       f"{self.rng.randint(1000, 9999)}",
            expiry=expiry,
            beginning_qty=qty,
            source_of_fund=self.rng.choice(ref.FUND_SOURCES),
            received=received,
        )
        self.batches.setdefault(med_id, []).append(b)
        return b

    def _restock(self, med_id: str, day: date, base: float) -> None:
        qty = int(base * self.rng.uniform(75, 120))
        b = self._new_batch(med_id, max(qty, 10), day)
        self._restock_seq += 1
        self.t.add("restock_log", {
            "restock_id": f"RST-{self._restock_seq:05d}",
            "medicine_id": med_id,
            "quantity_added": b.beginning_qty,
            "restocked_by": "supply.officer@ipho.example",
            "timestamp": _ts(day, self.rng),
            "batch_id": b.batch_id,
        })

    def _available(self, med_id: str, day: date) -> list[Batch]:
        live = [b for b in self.batches.get(med_id, [])
                if b.remaining > 0 and b.received <= day and (b.expiry is None or b.expiry > day)]
        return sorted(live, key=lambda b: b.expiry or date.max)  # FEFO

    # ── events ──────────────────────────────────────────────────────────
    def _event(self, name: str, category: str, day: date) -> str:
        self._event_seq += 1
        eid = f"EVT-{self._event_seq:05d}"
        release = day + timedelta(days=self.rng.choice([0, 0, 1, 2, 3]))
        self.t.add("distribution_event", {
            "event_id": eid,
            "event_name": name,
            "distribution_category": category,
            "event_date": _legacy_or_iso(day, self.rng),
            "doc_release_date": _legacy_or_iso(release, self.rng),
            "transaction_ref": f"TR-{day.year}-{self._event_seq:05d}",
        })
        return eid

    def _issue(self, event_id: str, med_id: str, qty: int, day: date) -> int:
        """Issue `qty` FEFO across batches; returns what was actually issued."""
        issued = 0
        for b in self._available(med_id, day):
            if issued >= qty:
                break
            take = min(b.remaining, qty - issued)
            b.remaining -= take
            issued += take
            self._dist_seq += 1
            self.t.add("distribution", {
                "distribution_id": f"DST-{self._dist_seq:06d}",
                "batch_id": b.batch_id,
                "event_id": event_id,
                "qty_dispensed": take,
            })
            if self.rng.random() < 0.004:
                # returned partially (wrong item / damaged on arrival)
                back = max(1, take // self.rng.randint(4, 10))
                b.remaining += back
                self._return_seq += 1
                self.t.add("returns", {
                    "return_id": f"RET-{self._return_seq:05d}",
                    "distribution_id": f"DST-{self._dist_seq:06d}",
                    "batch_id": b.batch_id,
                    "event_id": event_id,
                    "qty_returned": back,
                    "returned_by": "supply.officer@ipho.example",
                    "timestamp": _ts(day + timedelta(days=self.rng.randint(1, 10)), self.rng),
                    "notes": self.rng.choice(["Damaged on arrival", "Wrong item", "Excess"]),
                })
        if issued == 0 and self.rng.random() < 0.05:
            # bad row: zero-quantity line encoded anyway
            self._dist_seq += 1
            any_batch = self.batches[med_id][-1]
            self.t.add("distribution", {
                "distribution_id": f"DST-{self._dist_seq:06d}",
                "batch_id": any_batch.batch_id,
                "event_id": event_id,
                "qty_dispensed": 0,
            })
        return issued

    def _demand(self, med_id: str, day: date, days_covered: float, share: float) -> int:
        _, _, _, cls, base = self.meds[med_id]
        lam = base * ref.SEASONALITY[cls][day.month - 1] * _trend(day) * days_covered * share
        noisy = self.rng.gauss(lam, math.sqrt(max(lam, 1)) * 1.3)
        return max(0, int(round(noisy)))

    # ── main loop ───────────────────────────────────────────────────────
    def run(self) -> Tables:
        for med_id, (_desc, _uom, _price, _cls, base) in self.meds.items():
            for _ in range(self.rng.randint(1, 3)):
                self._new_batch(med_id, int(base * self.rng.uniform(90, 160)), START)

        municipalities = list(ref.MUNICIPALITIES.items())
        day = START
        while day <= END:
            # Restock check every Monday: reorder when < ~30 days of cover remain.
            if day.weekday() == 0:
                for med_id, (_, _, _, _cls, base) in self.meds.items():
                    on_hand = sum(b.remaining for b in self._available(med_id, day))
                    if on_hand < base * 30 * _trend(day) and self.rng.random() < 0.85:
                        self._restock(med_id, day, base)

            # Monthly allocation to every municipality's RHU (first weekday after the 5th).
            if day.day == 6 or (day.day in (7, 8) and day.weekday() == 0):
                if not any(r["event_name"].endswith(day.strftime("%b %Y"))
                           for r in self.t.rows.get("distribution_event", [])[-20:]):
                    for muni, share in municipalities:
                        eid = self._event(f"Allocation - RHU {muni} - {day:%b %Y}",
                                          "Allocation", day)
                        for med_id in self.meds:
                            if self.rng.random() < 0.7:
                                self._issue(eid, med_id,
                                            self._demand(med_id, day, 30 * 0.6, share), day)

            # School deworming MDO rounds in January and July.
            if day.month in (1, 7) and day.day == 20:
                for muni, share in municipalities:
                    eid = self._event(f"MDO Deworming - {muni} - {day:%b %Y}", "MDO", day)
                    for med_id in ("MED-027", "MED-028", "MED-035"):
                        self._issue(eid, med_id, self._demand(med_id, day, 30, share * 2), day)

            # Ad-hoc requests from hospitals/RHUs, ~2 per week.
            if day.weekday() < 5 and self.rng.random() < 0.4:
                muni, share = self.rng.choices(municipalities,
                                               weights=[s for _, s in municipalities])[0]
                eid = self._event(f"Request - {muni} District Hospital - {day:%Y-%m-%d}",
                                  "Request", day)
                for med_id in self.rng.sample(list(self.meds), self.rng.randint(2, 6)):
                    self._issue(eid, med_id, self._demand(med_id, day, 7, share), day)

            # Weekly OPD replenishment (pre-dates the clinic app's own dispensing log).
            if day.weekday() == 4:
                eid = self._event(f"OPD - IPHO Clinic - week of {day:%Y-%m-%d}", "OPD", day)
                for med_id in self.meds:
                    if self.rng.random() < 0.5:
                        self._issue(eid, med_id, self._demand(med_id, day, 7, 0.05), day)

            day += timedelta(days=1)

        self._finalize()
        return self.t

    def _finalize(self) -> None:
        issued_per_batch: dict[str, int] = {}
        for r in self.t.rows["distribution"]:
            issued_per_batch[r["batch_id"]] = issued_per_batch.get(r["batch_id"], 0) \
                + int(r["qty_dispensed"])

        med_totals: dict[str, list[int]] = {}
        for med_id, batches in self.batches.items():
            for b in batches:
                dispensed = issued_per_batch.get(b.batch_id, 0)
                self.t.add("batch", {
                    "batch_id": b.batch_id,
                    "medicine_id": med_id,
                    "store_room": b.store_room,
                    "lot_number": b.lot_number,
                    "expiry_date": _legacy_or_iso(b.expiry, self.rng) if b.expiry else "",
                    "beginning_qty": b.beginning_qty,
                    "ending_qty": b.remaining,
                    "total_dispensed": dispensed,
                    "current_qty": b.remaining,
                    "source_of_fund": b.source_of_fund,
                })
                t = med_totals.setdefault(med_id, [0, 0, 0])
                t[0] += b.beginning_qty
                t[1] += dispensed
                t[2] += b.remaining

        for med_id, (desc, uom, price, _cls, _base) in self.meds.items():
            beg, disp, cur = med_totals[med_id]
            self.t.add("medicine", {
                "medicine_id": med_id,
                "description": desc,
                "unit_of_measure": uom,
                "unit_price": price,
                "beginning_qty": beg,
                "total_dispensed": disp,
                "current_qty": cur,
                # Movement metrics are recomputed downstream; leave app defaults.
                "dispense_rate": 0,
                "event_frequency": 0,
                "consumption_ratio": 0,
                "composite_score": 0,
                "movement_category": "Non-Moving",
            })


class ClinicGenerator:
    def __init__(self, rng: random.Random, meds: dict[str, tuple]) -> None:
        self.rng = rng
        self.meds = meds
        self.t = Tables()
        self._by_class: dict[str, list[str]] = {}
        for med_id, (_desc, _uom, _price, cls, _base) in meds.items():
            self._by_class.setdefault(cls, []).append(med_id)

    def _patient(self, n: int) -> dict:
        r = self.rng
        sex = r.choice(["Male", "Female"])
        first = r.choice(ref.FIRST_NAMES_M if sex == "Male" else ref.FIRST_NAMES_F)
        muni = r.choices(list(ref.MUNICIPALITIES), weights=list(ref.MUNICIPALITIES.values()))[0]
        age = int(min(95, max(0, r.gauss(38, 20))))
        created = START + timedelta(days=r.randint(0, (END - START).days))
        return {
            "patient_id": f"PT{n:06d}",
            "last_name": r.choice(ref.LAST_NAMES),
            "first_name": first,
            "middle_name": r.choice(ref.LAST_NAMES) if r.random() < 0.8 else "",
            "suffix": r.choice(["", "", "", "", "Jr.", "III"]) if sex == "Male" else "",
            "sex": sex,
            "birthdate": (date(2026, 1, 1) - timedelta(days=age * 365 + r.randint(0, 364)))
                         .isoformat(),
            "civil_status": r.choice(ref.CIVIL_STATUS) if age >= 18 else "Single",
            "occupation": r.choice(ref.OCCUPATIONS) if age >= 18 else "Student",
            "address": f"Purok {r.randint(1, 9)}",
            "barangay": r.choice(ref.BARANGAY_SUFFIXES),
            "municipality": muni,
            "contact_number": f"09{r.randint(100000000, 999999999)}" if r.random() < 0.85 else "",
            "philhealth_no": f"{r.randint(10, 19)}-{r.randint(100000000, 999999999)}-"
                             f"{r.randint(0, 9)}" if r.random() < 0.6 else "",
            "created_at": _ts(created, r),
            "created_by": r.choice(ref.CLINIC_STAFF),
            "updated_at": _ts(created, r),
            "_created": created,  # internal, stripped before writing
        }

    def run(self, n_patients: int = 3200) -> Tables:
        patients = [self._patient(i + 1) for i in range(n_patients)]
        patients.sort(key=lambda p: p["_created"])
        visit_seq = disp_seq = item_seq = 0

        day = START
        while day <= END:
            if day.weekday() < 5:
                eligible = [p for p in patients if p["_created"] <= day]
                n_visits = max(0, int(self.rng.gauss(14 * _trend(day), 4)))
                for _ in range(min(n_visits, len(eligible))):
                    p = self.rng.choice(eligible)
                    weights = [
                        w * (ref.SEASONALITY.get(season, [1.0] * 12)[day.month - 1])
                        for w, (_, _, _, season)
                        in zip(ref.DIAGNOSIS_WEIGHTS, ref.DIAGNOSES, strict=True)
                    ]
                    canonical, variants, classes, _ = self.rng.choices(ref.DIAGNOSES, weights)[0]
                    visit_seq += 1
                    vid = f"V{visit_seq:06d}"
                    feverish = canonical in ("Dengue fever", "Community-acquired pneumonia",
                                             "Acute upper respiratory infection")
                    self.t.add("visits", {
                        "visit_id": vid,
                        "patient_id": p["patient_id"],
                        "visit_date": day.isoformat(),
                        "chief_complaint": self.rng.choice(
                            ["fever", "cough", "headache", "follow-up", "body malaise",
                             "abdominal pain", "dizziness", "medicine refill"]),
                        "diagnosis": self.rng.choice(variants),
                        "attending_staff": self.rng.choice(ref.CLINIC_STAFF),
                        "blood_pressure": f"{self.rng.randint(100, 165)}/"
                                          f"{self.rng.randint(60, 105)}"
                                          if self.rng.random() < 0.8 else "",
                        "temperature_c": round(self.rng.uniform(37.8, 39.6) if feverish
                                               else self.rng.uniform(36.2, 37.3), 1)
                                         if self.rng.random() < 0.9 else "",
                        "notes": "",
                        "created_at": _ts(day, self.rng),
                        "created_by": self.rng.choice(ref.CLINIC_STAFF),
                    })
                    if self.rng.random() < 0.85:
                        disp_seq += 1
                        did = f"DSP{disp_seq:06d}"
                        self.t.add("dispensing_records", {
                            "dispensing_id": did,
                            "visit_id": vid,
                            "patient_id": p["patient_id"],
                            "dispensed_by": self.rng.choice(ref.CLINIC_STAFF),
                            "dispensed_at": _ts(day, self.rng),
                            "notes": "",
                        })
                        pool = [m for c in classes for m in self._by_class.get(c, [])]
                        for med_id in self.rng.sample(pool, min(len(pool),
                                                                self.rng.randint(1, 3))):
                            item_seq += 1
                            self.t.add("dispensing_items", {
                                "item_id": item_seq,
                                "dispensing_id": did,
                                "medicine_id": med_id,
                                "medicine_name": self.meds[med_id][0],
                                "qty_dispensed": self.rng.choice([1, 5, 7, 10, 14, 15, 21, 30]),
                            })
            day += timedelta(days=1)

        for p in patients:
            p.pop("_created")
        self.t.rows["patients"] = patients
        return self.t


def write_tables(tables: Tables, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.rows.items():
        with (out_dir / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"  {out_dir.name}.{name:<20} {len(rows):>7,} rows")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=Path("data/source"))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--patients", type=int, default=3200)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    inv = InventoryGenerator(rng)
    print(f"Generating synthetic IPHO source data (seed={args.seed})")
    write_tables(inv.run(), args.out / "inventory")
    write_tables(ClinicGenerator(rng, inv.meds).run(args.patients), args.out / "clinic")


if __name__ == "__main__":
    main()
