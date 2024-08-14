from hakai_metadata_conversion.zenodo import zenodo
from hakai_metadata_conversion.__main__ import load
from glob import glob
import pytest

@pytest.mark.parametrize("file", glob("tests/records/**/*.yaml", recursive=True))
def test_zenodo_record(file):
    record = load(file, "yaml")
    result = zenodo(record)
    assert result
    