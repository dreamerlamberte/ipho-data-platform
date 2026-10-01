import pyarrow as pa
import pytest
from ipho_ingest.pii import apply_policy, pseudonymize

SALT = b"test-salt"


def _table():
    return pa.table({
        "patient_id": ["PT000001", "PT000002", ""],
        "last_name": ["Dela Cruz", "Santos", "Reyes"],
        "birthdate": ["1980-05-02", "2001-12-30", ""],
        "philhealth_no": ["12-345678901-2", "", ""],
        "municipality": ["Ipil", "Titay", "Naga"],
    })


def test_pseudonym_is_stable_and_salted():
    assert pseudonymize("PT000001", SALT) == pseudonymize("PT000001", SALT)
    assert pseudonymize("PT000001", SALT) != pseudonymize("PT000001", b"other")
    assert pseudonymize("PT000001", SALT) != "PT000001"


def test_policy_removes_direct_identifiers():
    out = apply_policy(_table(), {
        "patient_id": "hash", "last_name": "drop",
        "birthdate": "year_only", "philhealth_no": "presence",
    }, SALT)
    assert "last_name" not in out.column_names
    assert out.column("birthdate").to_pylist() == ["1980", "2001", ""]
    assert out.column("philhealth_no").to_pylist() == ["true", "false", "false"]
    ids = out.column("patient_id").to_pylist()
    assert "PT000001" not in ids and ids[2] == ""      # blanks stay blank, not hashed
    assert out.column("municipality").to_pylist() == ["Ipil", "Titay", "Naga"]


def test_policy_fails_loudly_on_schema_drift():
    with pytest.raises(KeyError):
        apply_policy(_table(), {"contact_number": "drop"}, SALT)
    with pytest.raises(ValueError):
        apply_policy(_table(), {"last_name": "encrypt"}, SALT)
