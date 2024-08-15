from glob import glob

import pytest

from hakai_metadata_conversion.__main__ import load
from hakai_metadata_conversion.zenodo import zenodo


@pytest.mark.parametrize("file", glob("tests/records/**/*.yaml", recursive=True))
def test_zenodo_record(file):
    record = load(file, "yaml")
    result = zenodo(record)
    assert result
