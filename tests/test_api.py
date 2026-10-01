"""API smoke tests against the warehouse built by `make pipeline`."""

import pytest
from fastapi.testclient import TestClient
from ipho_api.main import app
from ipho_api.settings import WAREHOUSE_PATH

pytestmark = pytest.mark.skipif(not WAREHOUSE_PATH.exists(),
                                reason="warehouse not built; run `make pipeline`")
client = TestClient(app)


def test_overview_and_inventory():
    ov = client.get("/api/overview").json()
    assert ov["weekly_visits"] and ov["top_diagnoses"]
    med = client.get("/api/medicines").json()[0]["medicine_id"]
    inv = client.get(f"/api/inventory/{med}").json()
    assert inv["daily"] and inv["kpis"]["on_hand"] >= 0
    assert client.get("/api/inventory/NOPE").status_code == 404


def test_surveillance_threshold():
    s = client.get("/api/surveillance", params={"diagnosis": "Dengue fever"}).json()
    assert s["weekly"][0]["threshold"] is None          # no baseline yet
    assert any(w["threshold"] is not None for w in s["weekly"])


def test_sql_is_sandboxed():
    ok = client.post("/api/sql", json={"sql": "select count(*) as n from gold.dim_medicine"})
    assert ok.status_code == 200 and ok.json()["rows"][0][0] > 0
    for bad in ["drop table gold.dim_medicine",
                "select * from read_csv('/etc/passwd')",
                "select 1; drop table gold.dim_medicine"]:
        assert client.post("/api/sql", json={"sql": bad}).status_code == 400


def test_pipeline_control_disabled_by_default():
    assert client.post("/api/pipeline/run", json={"stage": "all"}).status_code == 403
