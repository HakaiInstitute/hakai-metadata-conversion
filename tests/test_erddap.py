from glob import glob

import pytest
from lxml import etree

import hakai_metadata_conversion.erddap as erddap
from hakai_metadata_conversion.__main__ import load

@pytest.mark.core
def test_erddap_global_attributes(record):
    result = erddap.global_attributes(record, output=None, language="en")
    assert result
    assert isinstance(result, dict)
    assert "title" in result
    assert "summary" in result
    assert "project" in result
    assert "keywords" in result
    assert "id" in result
    assert "naming_authority" in result
    assert "date_modified" in result
    assert "date_created" in result
    assert "product_version" in result
    assert "history" in result
    assert "license" in result
    assert "creator_name" in result
    assert "creator_institution" in result
    assert "creator_address" in result
    assert "creator_city" in result
    assert "creator_country" in result
    assert "creator_url" in result
    assert "publisher_name" in result
    assert "publisher_institution" in result
    assert "publisher_address" in result
    assert "publisher_city" in result
    assert "publisher_country" in result
    assert "publisher_url" in result
    assert "metadata_link" in result

@pytest.mark.core
def test_erddap_global_attributes_xml(record):
    result = erddap.global_attributes(record, output="xml", language="en")
    assert result


class TestDatasetXmlEscaping:
    """The generated dataset.xml has to be well-formed XML.

    It is built by string concatenation to keep its existing shape, so nothing
    escapes markup characters unless _generate_dataset_xml does. Before it did,
    an abstract containing "RGB & NIR" or "< 0.5% to > 5 %" produced a file
    ERDDAP could not load - 49 of the 317 committed records were affected.
    """

    @pytest.mark.core
    @pytest.mark.parametrize(
        "value",
        [
            "RGB & NIR",
            "< 0.5% to > 5 % body weight",
            "a rapid >90% decline",
            "Fish & Wildlife <Branch>",
            "quotes ' and \" together",
            "already escaped &amp; stays distinct",
        ],
    )
    def test_values_survive_as_well_formed_xml(self, value):
        xml = erddap._generate_dataset_xml({"summary": value})
        root = etree.fromstring(xml.encode("utf-8"))
        assert root.find("att").text == value

    @pytest.mark.core
    def test_markup_in_a_value_cannot_inject_elements(self):
        """A value is text, never structure."""
        xml = erddap._generate_dataset_xml(
            {"summary": "</att><att name='license'>stolen</att>"}
        )
        root = etree.fromstring(xml.encode("utf-8"))
        assert [att.get("name") for att in root.findall("att")] == ["summary"]

    @pytest.mark.core
    def test_attribute_names_are_escaped(self):
        xml = erddap._generate_dataset_xml({"od&d'key": "value"})
        root = etree.fromstring(xml.encode("utf-8"))
        assert root.find("att").get("name") == "od&d'key"

    @pytest.mark.core
    def test_multilingual_values_are_escaped(self):
        xml = erddap._generate_dataset_xml(
            {"title": "A & B"},
            {"title": {"en": "A & B", "fr": "A < B"}},
        )
        root = etree.fromstring(xml.encode("utf-8"))
        assert [att.text for att in root.findall("att")] == ["A & B", "A & B", "A < B"]


@pytest.mark.metadataFiles
@pytest.mark.parametrize(
    "file",
    list(set(glob("tests/records/hakai-metadata-entry-form-files/**/*.yaml", recursive=True))
         - set(glob("tests/records/hakai-metadata-entry-form-files/unpublished/**/*.yaml", recursive=True))),
)
def test_cioos_metadata_files_to_erddap_xml(file):
    data = load(file, "CIOOS")
    result = erddap.global_attributes(data, output="xml", language="en")

    assert result
    # Parses rather than just being truthy: a non-empty string that ERDDAP
    # cannot load is exactly the failure this is guarding against.
    etree.fromstring(result.strip().encode("utf-8"))

def test_erddap_global_attributes_xml_multilingual_suffix(record):
    result = erddap.global_attributes(record, output=None, language="en", multilingual="suffix")

    assert result
    assert isinstance(result, dict)
    assert "title" in result
    assert "summary" in result
    assert "title_fr" in result
    assert "title_en" in result
    assert "summary_fr" in result
    assert "summary_en" in result


def test_erddap_global_attributes_xml_multilingual_nested(record):
    result = erddap.global_attributes(record, output=None, language="en", multilingual="nested")

    assert result
    assert isinstance(result, dict)
    assert "title" in result
    assert "summary" in result
    assert "(en)" in result["title"]
    assert "(fr)" in result["title"]
    assert "(en)" in result["summary"]
    assert "(fr)" in result["summary"]
    assert "title_fr" not in result
    assert "title_en" not in result
    assert "summary_fr" not in result
    assert "summary_en" not in result


def test_erddap_global_attributes_xml_multilingual_xml(record):
    result = erddap.global_attributes(
        record, output="xml", language="en", multilingual="xml"
    )

    assert result
    assert isinstance(result, str)
    assert "<att name='title' xml:lang='en'>" in result
    assert "<att name='title' xml:lang='fr'>" in result
    assert "<att name='summary' xml:lang='en'>" in result
    assert "<att name='summary' xml:lang='fr'>" in result


@pytest.mark.metadataFiles
@pytest.mark.parametrize(
    "file",
    list(set(glob("tests/records/hakai-metadata-entry-form-files/**/*.yaml", recursive=True))
         - set(glob("tests/records/hakai-metadata-entry-form-files/unpublished/**/*.yaml", recursive=True))),
)
def test_cioos_metadata_files_to_erddap_fr(file):
    data = load(file, "CIOOS")
    result_fr = erddap.global_attributes(data, output="xml", language="fr")

    assert result_fr

@pytest.mark.core
def test_erddap_dataset_xml_update(record, tmp_path):
    erddap.update_dataset_xml(
        "tests/erddap_xmls/test_datasets.xml",
        [record],
        erddap_url="https://catalogue.cioos.org/erddap",
        output_dir=tmp_path,
    )
    assert (tmp_path / "test_datasets.xml").exists()

@pytest.mark.core
def test_erddap_dataset_xml_update_string(tmp_path):
    erddap.update_dataset_xml(
        "tests/erddap_xmls/test_datasets.xml",
        "tests/records/*.yaml",
        erddap_url="https://catalogue.cioos.org/erddap",
        output_dir=tmp_path,
    )
    assert (tmp_path / "test_datasets.xml").exists()

@pytest.mark.core
def test_erddap_dataset_d_xml_update(record, tmp_path):
    erddap.update_dataset_xml(
        "tests/erddap_xmls/datasets.d/*.xml",
        [record],
        erddap_url="https://catalogue.cioos.org/erddap",
        output_dir=tmp_path,
    )
    files = tmp_path.glob("dataset.d/*.xml")
    assert files


def test_erddap_dataset_d_xml_update_multilangual(record, tmp_path):
    erddap.update_dataset_xml(
        "tests/erddap_xmls/datasets.d/*.xml",
        [record],
        erddap_url="https://catalogue.cioos.org/erddap",
        output_dir=tmp_path,
        multilingual=True,
    )
    files = tmp_path.glob("dataset.d/*.xml")
    assert files
    for file in files:
        with open(file, "r") as f:
            content = f.read()
            assert "xml:lang" in content
