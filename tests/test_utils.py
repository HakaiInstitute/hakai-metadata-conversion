import pytest

from hakai_metadata_conversion.utils import camel_to_title, get_path


@pytest.mark.parametrize(
    "inp, expected",
    [
        ("", ""),
        (None, ""),  # gracefully handles None via 'if not s'
        ("surfaceTemperature", "Surface Temperature"),
        ("SurfaceTemperature", "Surface Temperature"),
        ("httpServerError", "Http Server Error"),
        ("sea_surface_temperature", "Sea Surface Temperature"),
        ("sea--surface__TEMP", "Sea Surface TEMP"),
        ("Single", "Single"),
        ("Already Spaced", "Already Spaced"),
        ("version2ID", "Version2 ID"),
        ("gpsLAT", "Gps LAT"),
        ("a", "A"),
        ("A", "A"),
        ("APIResponseOK", "API Response OK"),
    ],
)
def test_camel_to_title_various(inp, expected):
    assert camel_to_title(inp) == expected


def test_acronym_preservation():
    assert camel_to_title("NASADataAPI") == "NASA Data API"


def test_multiple_separators_collapsed():
    assert camel_to_title("multi___part---Value") == "Multi Part Value"


def test_idempotency_on_output():
    # Running twice should not change result
    s = "subSurfaceTemperature"
    assert camel_to_title(camel_to_title(s)) == camel_to_title(s)


def test_get_path_handles_missing_hops():
    assert get_path({"feed": {"url": "u"}}, "feed.url") == "u"
    assert get_path({"feed": {}}, "feed.url") is None
    assert get_path({}, "feed.url") is None
    assert get_path({"feed": "not-a-dict"}, "feed.url") is None


def test_get_path_single_hop_and_deep_path():
    assert get_path({"a": 1}, "a") == 1
    assert get_path({"a": {"b": {"c": "deep"}}}, "a.b.c") == "deep"
    assert get_path({"a": {"b": {}}}, "a.b.c") is None


def test_get_path_returns_default_for_missing_and_null():
    assert get_path({}, "metadata.language", "en") == "en"
    assert get_path({"metadata": {}}, "metadata.language", "en") == "en"
    # An explicit null in the YAML is treated as absent, so callers that pass a
    # default get it rather than a None they'd have to guard against.
    assert get_path({"metadata": {"language": None}}, "metadata.language", "en") == "en"


def test_get_path_preserves_falsy_values():
    # Only None counts as missing: "" and 0 are real values the record set.
    assert get_path({"a": {"b": ""}}, "a.b", "fallback") == ""
    assert get_path({"a": {"b": 0}}, "a.b", "fallback") == 0
    assert get_path({"a": {"b": []}}, "a.b", "fallback") == []
