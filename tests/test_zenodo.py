from glob import glob
import os
import json
import time

import pytest
import requests

from hakai_metadata_conversion.__main__ import load
from hakai_metadata_conversion.zenodo import zenodo

ZENODO_TOKEN = os.getenv("ZENODO_ACCESS_TOKEN")
RATE_LIMIT = 1 # delay between requests

@pytest.mark.parametrize("file", glob("tests/records/**/*.yaml", recursive=True))
def test_zenodo_record(file):
    record = load(file, "yaml")
    result = zenodo(record)
    assert result

@pytest.mark.skipif(not ZENODO_TOKEN, reason="ZENODO_ACCESS_TOKEN not set")
@pytest.mark.parametrize("file", glob("tests/records/**/*.yaml", recursive=True))
def test_zenodo_submission(file):
    record = load(file, "yaml")
    result = zenodo(record)
    time.sleep(RATE_LIMIT)
    response = requests.put(
        "https://sandbox.zenodo.org/api/deposit/depositions/100611",
        data=json.dumps({"metadata": result}),
        params={"access_token": ZENODO_TOKEN},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code in (200, 201), response.text
    assert response.json()
