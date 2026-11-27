from pathlib import Path

import pytest

from hakai_metadata_conversion.record import Record

Path("tests/results").mkdir(exist_ok=True)

# tests/records/firebase holds one firebase record per file, with one exception:
# the RTDB dump that test_firebase_regeneration.py reads. That file is the whole
# database keyed by region (hakai.users.<uid>.records.<id>), not a record, so the
# tests that glob for record-shaped json have to leave it out or they try to
# convert the database itself and fail on the missing record keys.
FIREBASE_DB_EXPORT = "cioos-metadata-form-export.json"


def firebase_record_files(root, pattern="*.json"):
    """Record-shaped json under `root`, skipping the whole-database dump."""
    return sorted(p for p in Path(root).glob(pattern) if p.name != FIREBASE_DB_EXPORT)


@pytest.fixture
def record_file_yaml():
    return "tests/records/test_record1.yaml"


def test_record_file_yaml(record_file_yaml):
    assert Path(record_file_yaml).exists()
    assert record_file_yaml.endswith((".yaml", ".yml"))


@pytest.fixture
def record(record_file_yaml):
    record = Record(record_file_yaml, "CIOOS")
    record.load()
    record.convert_to_cioos_schema()
    return record.metadata
