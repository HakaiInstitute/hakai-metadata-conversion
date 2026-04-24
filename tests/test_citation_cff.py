import subprocess
from glob import glob

import pytest

from hakai_metadata_conversion import citation_cff
from hakai_metadata_conversion.__main__ import load
from hakai_metadata_conversion.citation_cff import _get_unique_authors

@pytest.mark.core
def test_citation_cff(record):
    result = citation_cff.citation_cff(record, output_format=None, language="en")
    print(result)
    assert result
    assert isinstance(result, dict)
    assert "cff-version" in result
    assert "date-released" in result
    assert "contact" in result
    assert "authors" in result
    assert "identifiers" in result
    assert "keywords" in result
    assert "license" in result
    assert "license-url" in result
    assert "message" in result
    assert "type" in result
    assert "url" in result
    assert "version" in result
    assert "identifiers" in result

@pytest.mark.core
def test_ctation_cff_yaml(record, tmp_path):
    result = citation_cff.citation_cff(record, output_format="yaml", language="en")
    (tmp_path / "CITATION.cff").write_text(result, encoding="utf-8")

@pytest.mark.core
def test_citation_cff_validation(record, tmp_path):

    result = citation_cff.citation_cff(record, output_format="yaml", language="en")
    (tmp_path / "CITATION.cff").write_text(result, encoding="utf-8")
    # run cffconvert validate cli
    result = subprocess.run(
        ["cffconvert", "--validate", "-i", str(tmp_path / "CITATION.cff")],
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.metadataFiles
@pytest.mark.parametrize(
    "file",
    list(set(glob("tests/records/hakai-metadata-entry-form-files/**/*.yaml", recursive=True))
         - set(glob("tests/records/hakai-metadata-entry-form-files/unpublished/**/*.yaml", recursive=True))),
)
def test_hakai_metadata_entry_form_files_cff(file, tmp_path):
    data = load(file, "yaml")
    result = citation_cff.citation_cff(data, output_format="yaml", language="en")
    assert result

    print(result)
    # validate cff
    (tmp_path / "CITATION.cff").write_text(result, encoding="utf-8")
    validation_result = subprocess.run(
        ["cffconvert", "--validate", "-i", str(tmp_path / "CITATION.cff")],
        capture_output=True,
    )
    assert validation_result.returncode == 0, validation_result.stderr.decode("utf-8")

@pytest.mark.metadataFiles
@pytest.mark.parametrize(
    "file",
        list(set(glob("tests/records/hakai-metadata-entry-form-files/**/*.yaml", recursive=True))
         - set(glob("tests/records/hakai-metadata-entry-form-files/unpublished/**/*.yaml", recursive=True))),
)
def test_hakai_metadata_entry_form_files_cff_fr(file, tmp_path):
    data = load(file, "yaml")
    result_fr = citation_cff.citation_cff(data, output_format="yaml", language="fr")
    assert result_fr

    # validate cff
    (tmp_path / "CITATION.cff").write_text(result_fr, encoding="utf-8")
    validation_result = subprocess.run(
        ["cffconvert", "--validate", "-i", str(tmp_path / "CITATION.cff")],
        capture_output=True,
    )
    assert validation_result.returncode == 0, validation_result.stderr.decode("utf-8")






def _make_record(contacts):
    return {"contact": contacts}


def _person_contact(roles, in_citation=True):
    return {
        "inCitation": in_citation,
        "roles": roles,
        "individual": {"name": "Smith, John", "email": "john@example.com"},
        "organization": {"name": "Test Org"},
    }


def _org_contact(roles, in_citation=True, org_name="Test Org"):
    return {
        "inCitation": in_citation,
        "roles": roles,
        "organization": {"name": org_name},
    }


@pytest.mark.core
def test_empty_contacts():
    assert _get_unique_authors(_make_record([])) == []

@pytest.mark.core
def test_excludes_not_in_citation():
    record = _make_record([_person_contact(["author"], in_citation=False)])
    assert _get_unique_authors(record) == []

@pytest.mark.core
def test_excludes_non_author_roles():
    record = _make_record([_person_contact(["distributor", "pointOfContact"])])
    assert _get_unique_authors(record) == []

@pytest.mark.core
def test_includes_author_role():
    contact = _person_contact(["author"])
    result = _get_unique_authors(_make_record([contact]))
    assert len(result) == 1
    assert result[0]["family-names"] == "Smith"
    assert result[0]["given-names"] == "John"

@pytest.mark.core
def test_includes_coauthor_role():
    contact = _person_contact(["coAuthor"])
    result = _get_unique_authors(_make_record([contact]))
    assert len(result) == 1

@pytest.mark.core
def test_deduplicates_identical_authors():
    contact = _person_contact(["author"])
    result = _get_unique_authors(_make_record([contact, contact]))
    assert len(result) == 1

@pytest.mark.core
def test_mixed_contacts():
    contacts = [
        _person_contact(["author"]),
        _person_contact(["distributor"], in_citation=True),
        _person_contact(["coAuthor"], in_citation=False),
        _org_contact(["coAuthor"], in_citation=True, org_name="Collab Org"),
    ]
    result = _get_unique_authors(_make_record(contacts))
    assert len(result) == 2

@pytest.mark.core
def test_organization_author():
    contact = _org_contact(["author"], org_name="University of Test")
    result = _get_unique_authors(_make_record([contact]))
    assert len(result) == 1
    assert result[0]["name"] == "University of Test"

@pytest.mark.core
def test_preserves_order():
    contacts = [
        _person_contact(["author"]),
        _org_contact(["coAuthor"], org_name="Second Org"),
    ]
    result = _get_unique_authors(_make_record(contacts))
    assert result[0]["family-names"] == "Smith"
    assert result[1]["name"] == "Second Org"