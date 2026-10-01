import random

from ipho_synth.generate import ClinicGenerator, InventoryGenerator


def test_inventory_is_deterministic_and_consistent():
    a = InventoryGenerator(random.Random(7)).run().rows
    b = InventoryGenerator(random.Random(7)).run().rows
    assert len(a["distribution"]) == len(b["distribution"]) > 1000

    # every batch's current_qty = beginning - issued + returned (what the app's triggers enforce)
    issued, returned = {}, {}
    for r in a["distribution"]:
        issued[r["batch_id"]] = issued.get(r["batch_id"], 0) + int(r["qty_dispensed"])
    for r in a["returns"]:
        returned[r["batch_id"]] = returned.get(r["batch_id"], 0) + int(r["qty_returned"])
    for bt in a["batch"]:
        expected = bt["beginning_qty"] - issued.get(bt["batch_id"], 0) \
            + returned.get(bt["batch_id"], 0)
        assert bt["current_qty"] == expected >= 0


def test_clinic_references_are_valid():
    inv = InventoryGenerator(random.Random(1))
    inv.run()
    t = ClinicGenerator(random.Random(1), inv.meds).run(n_patients=200).rows
    patient_ids = {p["patient_id"] for p in t["patients"]}
    assert all(v["patient_id"] in patient_ids for v in t["visits"])
    assert all(i["medicine_id"] in inv.meds for i in t["dispensing_items"])
