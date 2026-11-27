"""Vocabulary handling in the firebase -> CIOOS conversion.

Both behaviours here were found by test_firebase_regeneration.py: regenerating
the committed hakai outputs from the firebase export showed nine published
records quietly losing data.
"""

import pytest
from loguru import logger

from hakai_metadata_conversion.firebase_to_cioos import (
    UnknownVocabularyError,
    _resolve_licence,
    _sanitize_keyword_list,
    licenses,
    record_json_to_yaml,
)


@pytest.fixture
def logged_errors():
    """Collect ERROR messages emitted through loguru.

    pytest's caplog only sees the stdlib logging module, and this package logs
    through loguru, so an assertion built on caplog passes whether or not the
    log line exists. A sink captures the real thing - which matters here,
    because the error is the only signal a dropped licence produces in
    non-strict mode.
    """
    messages = []
    sink = logger.add(messages.append, level="ERROR", format="{message}")
    yield messages
    logger.remove(sink)


class TestKeywordSanitizing:
    """Keywords must survive sanitizing with their orthography intact.

    The character class is there to keep CKAN tag validation happy, but it was
    stripping characters out of the middle of First Nations names.
    """

    @pytest.mark.parametrize(
        "keyword",
        [
            "Da’naxda’xw Awaetlala territory",
            "Gitga’at Territory",
            "Ka:'yu:'k't'h'/Che:k'tles7et'h' territory",
        ],
    )
    def test_first_nations_names_survive_unchanged(self, keyword):
        assert _sanitize_keyword_list([keyword]) == [keyword]

    def test_typographic_apostrophe_is_not_folded_to_ascii(self):
        """U+2019 is kept as itself rather than rewritten to '."""
        assert _sanitize_keyword_list(["Gitga’at"]) == ["Gitga’at"]

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("a|b", ["a", "b"]),
            ("a>b", ["a", "b"]),
            ("a\nb", ["a", "b"]),
            ("x &gt; y", ["x", "y"]),
            ("  padded  ", ["padded"]),
            ("dup,dup", ["dup,dup"]),
            # '<' is not a delimiter, only '>' is: this splits on the trailing
            # '>' and then drops the '<' as a disallowed character.
            ("tag<script>", ["tagscript"]),
        ],
    )
    def test_splitting_and_cleaning_still_applies(self, raw, expected):
        assert _sanitize_keyword_list([raw]) == expected

    def test_deduplicates_preserving_order(self):
        assert _sanitize_keyword_list(["b", "a", "b"]) == ["b", "a"]

    def test_non_strings_are_dropped(self):
        assert _sanitize_keyword_list(["ok", None, 3, {"a": 1}]) == ["ok"]


class TestLicenceResolution:
    """An unresolvable licence must be reported, never silently dropped."""

    def test_none_code_resolves(self):
        """Records store the licence `code`, not the map key.

        `licenses` is keyed by name for this entry ("No License") while every
        other key equals its own code, so records saying "None" missed and lost
        their licence entirely.
        """
        licence = _resolve_licence({"license": "None", "identifier": "x"})
        assert licence["code"] == "None"
        assert licence["url"] == "https://choosealicense.com/no-permission/"

    def test_none_and_no_license_resolve_to_the_same_licence(self):
        assert licenses["None"] == licenses["No License"]

    def test_known_code_resolves(self):
        assert _resolve_licence({"license": "CC-BY-4.0", "identifier": "x"})["code"] == (
            "CC-BY-4.0"
        )

    def test_absent_licence_is_not_an_error(self, logged_errors):
        """A record with no licence at all is normal, not a vocabulary miss."""
        assert _resolve_licence({"identifier": "x"}) is None
        assert _resolve_licence({"license": "", "identifier": "x"}) is None
        assert logged_errors == []

    def test_unknown_code_logs_an_error_and_returns_none(
        self, monkeypatch, logged_errors
    ):
        """The log line is the whole signal here, so assert on it.

        Without this, deleting the logger.error call would leave every other
        assertion in this class green and restore the silent licence loss.
        """
        monkeypatch.delenv("HAKAI_STRICT_VOCABULARY", raising=False)
        assert _resolve_licence({"license": "made-up", "identifier": "rec-1"}) is None
        assert len(logged_errors) == 1, logged_errors
        assert "made-up" in logged_errors[0]
        assert "rec-1" in logged_errors[0]

    def test_known_licence_logs_nothing(self, monkeypatch, logged_errors):
        monkeypatch.delenv("HAKAI_STRICT_VOCABULARY", raising=False)
        assert _resolve_licence({"license": "None", "identifier": "rec-1"})
        assert logged_errors == []

    def test_unknown_code_raises_under_strict(self, monkeypatch):
        monkeypatch.setenv("HAKAI_STRICT_VOCABULARY", "true")
        with pytest.raises(UnknownVocabularyError, match="made-up"):
            _resolve_licence({"license": "made-up", "identifier": "rec-1"})

    def test_strict_flag_is_read_per_call(self, monkeypatch):
        """Set at call time, not import time, so a caller can flip it."""
        monkeypatch.setenv("HAKAI_STRICT_VOCABULARY", "false")
        assert _resolve_licence({"license": "made-up", "identifier": "x"}) is None
        monkeypatch.setenv("HAKAI_STRICT_VOCABULARY", "TRUE")
        with pytest.raises(UnknownVocabularyError):
            _resolve_licence({"license": "made-up", "identifier": "x"})

    def test_known_licence_never_raises_under_strict(self, monkeypatch):
        monkeypatch.setenv("HAKAI_STRICT_VOCABULARY", "true")
        assert _resolve_licence({"license": "None", "identifier": "x"})["code"] == "None"


def _minimal_record(**overrides):
    record = {
        "identifier": "0f8a1b2c-0000-0000-0000-000000000000",
        "language": "en",
        "region": "hakai",
        "userID": "u1",
        "recordID": "r1",
        "title": {"en": "A record"},
        "contacts": [],
        "distribution": [],
    }
    record.update(overrides)
    return record


class TestRecordConversion:
    """The two fixes as they land in a converted record."""

    def test_licence_reaches_use_constraints(self):
        converted = record_json_to_yaml(_minimal_record(license="None"))
        assert converted["metadata"]["use_constraints"]["licence"]["code"] == "None"

    def test_keywords_reach_identification_intact(self):
        converted = record_json_to_yaml(
            _minimal_record(keywords={"en": ["Gitga’at Territory"], "fr": []})
        )
        assert converted["identification"]["keywords"]["default"]["en"] == [
            "Gitga’at Territory"
        ]

    def test_unknown_licence_still_converts_the_rest_of_the_record(self, monkeypatch):
        """Non-strict is non-breaking: the record converts, minus the licence."""
        monkeypatch.setenv("HAKAI_STRICT_VOCABULARY", "false")
        converted = record_json_to_yaml(_minimal_record(license="made-up"))
        assert converted["identification"]["title"] == {"en": "A record"}
        assert "licence" not in converted["metadata"].get("use_constraints", {})
