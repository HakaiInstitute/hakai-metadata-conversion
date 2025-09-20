import json
import os
import time
from glob import glob

import pytest
import requests

from hakai_metadata_conversion.__main__ import load
from hakai_metadata_conversion.zenodo import zenodo

ZENODO_TOKEN = os.getenv("ZENODO_ACCESS_TOKEN")
ZENODO_SUBMISSION_TEST = os.getenv("ZENODO_SUBMISSION_TEST")
DEPOSIT_ID = os.getenv("DEPOSIT_ID")
RATE_LIMIT = 1  # delay between requests


@pytest.mark.parametrize("file", glob("tests/records/**/*.yaml", recursive=True))
def test_zenodo_record(file):
    record = load(file, "yaml")
    result = zenodo(record)
    assert result


@pytest.mark.skipif(not ZENODO_TOKEN, reason="ZENODO_ACCESS_TOKEN not set")
@pytest.mark.skipif(not ZENODO_SUBMISSION_TEST, reason="ZENODO_SUBMISSION_TEST not set")
@pytest.mark.skipif(not DEPOSIT_ID, reason="DEPOSIT_ID not set")
@pytest.mark.parametrize("file", glob("tests/records/**/*.yaml", recursive=True))
def test_zenodo_submission(file):
    record = load(file, "yaml")
    result = zenodo(record)
    time.sleep(RATE_LIMIT)
    response = requests.put(
        f"https://sandbox.zenodo.org/api/deposit/depositions/{DEPOSIT_ID}",
        data=json.dumps({"metadata": result}),
        params={"access_token": ZENODO_TOKEN},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code in (200, 201), response.text
    assert response.json()
