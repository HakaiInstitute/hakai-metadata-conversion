"""Check the committed hakai output files against the firebase export they came from.

`tests/records/hakai-metadata-entry-form-files/hakai` holds four files per record
(cff / erddap / xml / yaml) that were generated from the firebase entry form.
`tests/records/firebase/cioos-metadata-form-export.json` is a dump of that
database. These tests re-run the conversion and compare.

The committed files predate several conversion changes, so an exact match is not
expected everywhere. Each systematic difference is named in KNOWN_* below with
the reason it exists; anything outside those lists fails, which is the point -
the lists turn "these files are stale in known ways" into a check that catches
the moment they go stale in some NEW way.

Joining records to files
------------------------
Neither the firebase `filename` field nor the file stem is a usable key:
`filename` is absent on 146 of 371 records and stale on roughly half the rest
(titles were edited after the files were written), and the 5-character suffix on
the stem is not unique - four groups share `437d9`. The identifier inside each
committed `.yaml` is the only reliable join, so a group with no `.yaml` cannot be
matched at all.
"""

import copy
import json
import os
import re
from pathlib import Path

import pytest
import yaml
from deepdiff import DeepDiff

from hakai_metadata_conversion.record import Record

HAKAI_DIR = Path("tests/records/hakai-metadata-entry-form-files/hakai")
EXPORT = Path("tests/records/firebase/cioos-metadata-form-export.json")

pytestmark = [
    pytest.mark.metadataFiles,
    pytest.mark.skipif(
        not HAKAI_DIR.is_dir() or not EXPORT.is_file(),
        reason="needs the hakai-metadata-entry-form-files checkout and the firebase export",
    ),
]

# Groups with no .yaml, so nothing to join on. Both are housekeeping, not
# conversion problems:
#   quadra_biomarathon - published, but its full four-file set lives under
#       unpublished/hakai/; the pair here is a leftover.
#   mean_tidal_current - no record with that identifier exists in the export at
#       all, in any region or status. Orphaned output.
UNJOINABLE = {
    "the_quadra_biomarathon__year_r_6231a",
    "mean_tidal_current___coastal_b_15caa",
}

# Differences every record shows, because the conversion moved on after the
# files were written. Paths carry a DeepDiff kind prefix and have list indices
# collapsed to [*] so they aggregate.
# topic_category arrived with "fix: pass topic category from firebase schema to
# ISO XML" (5aa0a09); scope / metadataScope / resourceType alongside it.
#
# maintenance_note used to be listed here too, because the base_url pointed at
# cioos-siooc.github.io where every committed file says
# hakaiinstitute.github.io/hakai-metadata-entry-form. That was a wrong URL
# rather than an expected delta, and is fixed in firebase_to_cioos now.
KNOWN_CODE_DELTAS = {
    "dictionary_item_added|root['identification']['topic_category']",
    "dictionary_item_added|root['metadata']['metadataScope']",
    "dictionary_item_added|root['metadata']['resourceType']",
    "dictionary_item_added|root['metadata']['scope']",
}

# Two sets used to live here, for records this comparison caught losing data:
# four whose First Nations keywords were being stripped of U+2019 and ':', and
# five carrying license "None" whose licence was silently dropped. Both are
# fixed in firebase_to_cioos now, so those nine records regenerate cleanly and
# are covered by tests/test_firebase_to_cioos.py. They are gone from here rather
# than listed as expected - that is the point of the exercise.

# Records edited in firebase after their files were written, so the export no
# longer describes what is on disk - revision timestamps bumped, orcids
# corrected, resources added, one abstract rewritten. Data drift, not conversion
# drift; regenerating the files clears these.
#
# Each record lists the exact paths expected to differ, and the test compares
# against that set rather than accepting any difference. Allowing "something
# differs" would let a licence drop or a mangled keyword on one of these eleven
# pass unnoticed - which is the class of bug this whole module exists to catch.
# The full record set lives in docs/firebase-record-followups.md.
KNOWN_DRIFTED = {
    "bc_estuary_water_quality_monit_b9226": {
        "values_changed|root['metadata']['dates']['revision']",
    },
    "conductivity__temperature_and__86343": {
        "values_changed|root['contact'][*]['individual']['orcid']",
        "values_changed|root['metadata']['dates']['revision']",
    },
    "data_from_manuscript__distribu_d43a7": {
        "values_changed|root['metadata']['dates']['revision']",
    },
    "freezing_seawater_samples_alte_290a0": {
        "iterable_item_added|root['identification']['associated_resources'][*]",
        "values_changed|root['metadata']['dates']['revision']",
    },
    "hakai_institute_juvenile_salmo_6c449": {
        "values_changed|root['contact'][*]['individual']['orcid']",
        "values_changed|root['metadata']['dates']['revision']",
    },
    "juvenile_salmon_migration_dyna_1769a": {
        "values_changed|root['contact'][*]['individual']['orcid']",
        "values_changed|root['metadata']['dates']['revision']",
    },
    # Written 18 seconds before the record was first published, so the committed
    # yaml predates its own publication date.
    "late_pleistocene_and_early_hol_a161a": {
        "dictionary_item_added|root['metadata']['dates']['publication']",
    },
    "sea_star_microbiome_data_from__33c8c": {
        "iterable_item_added|root['identification']['associated_resources'][*]",
        "values_changed|root['metadata']['dates']['revision']",
    },
    "sea_stars_2024_experiment___en_31ac8": {
        "iterable_item_added|root['identification']['associated_resources'][*]",
        "values_changed|root['metadata']['dates']['revision']",
    },
    "size_fractionated_zooplankton__dbb33": {
        "iterable_item_added|root['identification']['associated_resources'][*]",
        "values_changed|root['metadata']['dates']['revision']",
    },
    "zooplankton_abundance_and_biom_39a83": {
        "dictionary_item_added|root['identification']['abstract']['translations']",
        "values_changed|root['identification']['abstract']['en']",
        "values_changed|root['metadata']['dates']['revision']",
    },
}

# ERDDAP attributes the committed files carry that the conversion no longer
# produces the same way. "remove metadata_link inpu and add kwargs to add as
# global attributes" (4445dea) deleted the infoUrl attribute outright and
# stopped deriving metadata_link from the catalogue URL - acdd now falls back to
# the record's own DOI.
KNOWN_ERDDAP_ATTRS = {"infoUrl", "metadata_link"}

# The only cff difference anywhere: 9 records whose `type` collapsed to
# "dataset". Everything the committed files express about resource kind -
# collection, report, service, software, text - is now flattened, which CFF
# itself does allow but loses what the entry form recorded.
KNOWN_CFF_TYPE_CHANGED = {
    "discrete_water_chemistry_measu_a7873",  # collection -> dataset
    "fraser_river_landslide_project_f25b0",  # report     -> dataset
    "geoconnections_model_applicati_53730",  # service    -> dataset
    "google_earth_engine_kelp_tool__2a92c",  # software   -> dataset
    "hakai_rpas__drone__operations__58290",  # text       -> dataset
    "high_resolution_coastal_carbon_e5e61",  # collection -> dataset
    "phytoplankton_and_zooplankton__a8f45",  # collection -> dataset
    "time_lapse_camera_imagery_of_c_82a3f",  # service    -> dataset
    "vertical_water_property_profil_94d21",  # collection -> dataset
}


def _published_by_identifier():
    export = json.loads(EXPORT.read_text(encoding="utf-8"))
    out = {}
    for user in export["hakai"]["users"].values():
        for record in (user.get("records") or {}).values():
            if record.get("status") == "published":
                out[record.get("identifier")] = record
    return out


def _groups():
    groups = {}
    for f in sorted(os.listdir(HAKAI_DIR)):
        stem, ext = os.path.splitext(f)
        groups.setdefault(stem, set()).add(ext.lstrip("."))
    return groups


def _pairs():
    """(stem, firebase record) for every group we can join."""
    published = _published_by_identifier()
    pairs = []
    for stem, exts in sorted(_groups().items()):
        if "yaml" not in exts:
            continue
        identifier = yaml.safe_load((HAKAI_DIR / f"{stem}.yaml").read_text(encoding="utf-8"))[
            "metadata"
        ]["identifier"]
        if identifier in published:
            pairs.append((stem, published[identifier]))
    return pairs


PAIRS = _pairs() if HAKAI_DIR.is_dir() and EXPORT.is_file() else []
STEMS = [stem for stem, _ in PAIRS]


def _to_cioos(record):
    converted = Record(source=dict(record), schema="firebase")
    converted.load()
    converted.convert_to_cioos_schema()
    return converted.metadata


def _convert(cioos, output_format):
    record = Record(source=copy.deepcopy(cioos), schema="CIOOS")
    record.load()
    return record.convert_to(output_format)


def _lines(text):
    return [line.rstrip() for line in text.strip().splitlines()]


def test_every_output_group_is_complete():
    """Each record should have all four outputs, or be a known incomplete pair."""
    incomplete = {
        stem: sorted(exts)
        for stem, exts in _groups().items()
        if exts != {"cff", "erddap", "xml", "yaml"}
    }
    assert set(incomplete) == UNJOINABLE, (
        f"unexpected incomplete output groups: "
        f"{ {k: v for k, v in incomplete.items() if k not in UNJOINABLE} }"
    )


def test_every_output_group_has_a_published_firebase_record():
    joinable = {stem for stem, exts in _groups().items() if "yaml" in exts}
    assert joinable - set(STEMS) == set(), (
        "committed outputs with no published firebase record: "
        f"{sorted(joinable - set(STEMS))}"
    )


def test_every_published_firebase_record_has_outputs():
    """Published records whose files are missing or filed under unpublished/."""
    missing = set(_published_by_identifier()) - {
        yaml.safe_load((HAKAI_DIR / f"{stem}.yaml").read_text(encoding="utf-8"))["metadata"][
            "identifier"
        ]
        for stem in STEMS
    }
    # 48014fde (Microbial Oceanography) and 6231af54 (Quadra Biomarathon) are
    # published but their files still sit under unpublished/hakai/.
    assert len(missing) == 2, f"published records with no hakai/ output: {sorted(missing)}"


@pytest.mark.parametrize("stem,record", PAIRS, ids=STEMS)
def test_firebase_record_reproduces_committed_yaml(stem, record):
    """firebase -> CIOOS yaml should match the committed yaml.

    Compared as parsed structures rather than text: the conversion dumps yaml
    without allow_unicode, so accented characters come back as \\xE9 escapes
    where the committed files hold literal UTF-8. That is a serialization
    difference only and would otherwise drown out every real one.
    """
    committed = yaml.safe_load((HAKAI_DIR / f"{stem}.yaml").read_text(encoding="utf-8"))
    regenerated = yaml.safe_load(_convert(_to_cioos(record), "yaml"))

    # verbose_level is left at its default on purpose: at 0 DeepDiff drops
    # values_changed entirely, which hides every edited field and makes this
    # assertion look far stronger than it is.
    diff = DeepDiff(committed, regenerated, ignore_order=True)
    unexplained = {
        path
        for kind, items in diff.items()
        for path in (
            f"{kind}|" + re.sub(r"\[\d+\]", "[*]", p)
            for p in (items.keys() if hasattr(items, "keys") else items)
        )
        if path not in KNOWN_CODE_DELTAS
    }

    expected = KNOWN_DRIFTED.get(stem, set())
    assert unexplained == expected, (
        f"{stem}: firebase differences are not what KNOWN_DRIFTED records.\n"
        f"  unexpected: {sorted(unexplained - expected)}\n"
        f"  no longer present (drop from the list): {sorted(expected - unexplained)}"
    )


@pytest.mark.parametrize("stem", STEMS)
def test_committed_yaml_reproduces_committed_cff(stem):
    committed = yaml.safe_load((HAKAI_DIR / f"{stem}.cff").read_text(encoding="utf-8"))
    source = Record(source=str(HAKAI_DIR / f"{stem}.yaml"), schema="CIOOS")
    source.load()
    source.convert_to_cioos_schema()
    regenerated = yaml.safe_load(source.convert_to("cff"))

    diff = DeepDiff(committed, regenerated, ignore_order=True)
    allowed = {"values_changed|root['type']"} if stem in KNOWN_CFF_TYPE_CHANGED else set()
    actual = {
        f"{kind}|" + re.sub(r"\[\d+\]", "[*]", p)
        for kind, items in diff.items()
        for p in (items.keys() if hasattr(items, "keys") else items)
    }
    assert actual == allowed, f"{stem} cff differs: {diff}"


@pytest.mark.parametrize("stem", STEMS)
def test_committed_yaml_reproduces_committed_erddap(stem):
    """Regenerating erddap from the committed yaml isolates converter changes.

    Starting from the yaml rather than firebase holds the source data fixed, so
    anything left is the conversion itself. Two allowances:
      - infoUrl / metadata_link, removed by 4445dea
      - attribute order: acdd now builds `comment` before `project`, where the
        committed files have them the other way round. Same attributes, same
        values, different position - compared as a sorted multiset.
    """
    source = Record(source=str(HAKAI_DIR / f"{stem}.yaml"), schema="CIOOS")
    source.load()
    source.convert_to_cioos_schema()

    def strip(lines):
        return sorted(
            line
            for line in lines
            if not any(f"<att name='{a}'>" in line for a in KNOWN_ERDDAP_ATTRS)
        )

    committed = strip(_lines((HAKAI_DIR / f"{stem}.erddap").read_text(encoding="utf-8")))
    regenerated = strip(_lines(source.convert_to("erddap")))
    assert committed == regenerated, (
        f"{stem} erddap differs beyond {sorted(KNOWN_ERDDAP_ATTRS)} and attribute order"
    )


@pytest.mark.parametrize("stem", STEMS)
def test_committed_yaml_reproduces_committed_xml(stem):
    """ISO 19115-3 output should hold the same elements as the committed file.

    Every record currently differs in element order only - CI_Date swaps
    revision/publication and PT_Locale swaps eng/fra. The output is
    deterministic across hash seeds, so this is a stable ordering change rather
    than dict/set iteration noise, and the line multiset still matches exactly.
    """
    source = Record(source=str(HAKAI_DIR / f"{stem}.yaml"), schema="CIOOS")
    source.load()
    source.convert_to_cioos_schema()

    committed = _lines((HAKAI_DIR / f"{stem}.xml").read_text(encoding="utf-8"))
    regenerated = _lines(source.convert_to("iso19115-3_xml"))
    assert sorted(committed) == sorted(regenerated), f"{stem} xml content differs"
