from hakai_metadata_conversion.zenodo import zenodo

def test_zenodo_record(record):
    result = zenodo(record)
    assert result
    