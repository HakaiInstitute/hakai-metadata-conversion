import os

from loguru import logger

from hakai_metadata_conversion.__version__ import version

# FIXME zenodo do not recognize organizations vs person
# The api docs is limited regarding that
# The ror field is not recognized by the api
RAISE_ERRORS = os.getenv("RAISE_ERRORS", False)

hakai_roles_to_zenodo_roles = {
    "pointOfContact": "ContactPerson",
    "custodian": "DataCurator",
    "distributor": "Distributor",
    "principalInvestigator": "ProjectLeader",
    "owner": "RightsHolder",
    "funder": "Sponsor",
    "processor": "Editor",
    "originator": "Producer",
    "author": "ProjectLeader",
    "coAuthor": "ProjectMember",
    "contributor": "RelatedPerson",
    "resourceProvider": "DataCollector",
    "publisher": "Distributor",
    "editor": "Editor",
    "collaborator": "RelatedPerson",
    "rightsHolder": "RightsHolder",
    "sponsor": "Sponsor",
}


def _get_contributor_role(contributor):
    roles = []
    for role in contributor.get("roles", []):
        if role in hakai_roles_to_zenodo_roles:
            roles.append(hakai_roles_to_zenodo_roles[role])
            continue
        if RAISE_ERRORS:
            raise ValueError(f"Role {role} not found in hakai_roles_to_zenodo_roles")
        logger.warning(f"Role {role} not found in hakai_roles_to_zenodo_roles")
        roles.append("Other")
    return set(roles)


def _get_creator(creator, role=None):
    if creator.get("individual", {}).get("name"):
        return _get_person(creator, role)
    return _get_organization(creator, role)


def _get_organization(organization, role=None):
    return {
        "name": organization.get("organization", {}).get("name"),
        "ror": organization.get("organization", {})
        .get("ror", "")
        .replace("https://ror.org/", ""),
        "affiliation": organization.get("organization", {}).get("name"),
        **({"type": role} if role else {}),
    }


def _get_person(person, role=None):
    return {
        "name": person.get("individual", {}).get("name"),
        "affiliation": person.get("organization", {}).get("name"),
        "orcid": person.get("individual", {}).get("orcid"),
        # "gnd": person.get("gnd")
        **({"type": role} if role else {}),
    }


def _get_creators(record):
    """Convert Hakai metadata creators to Zenodo format.

    Creators are the people or organizations that appear in the citation of the dataset.
    """
    return [
        _get_creator(creator) for creator in record["contact"] if creator["inCitation"]
    ]


def _get_contributors(record):
    """Convert Hakai metadata contributors to Zenodo format.

    Contributors are the contacts with their roles in the dataset.
    """
    return [
        _get_creator(contributor, role)
        for contributor in record["contact"]
        for role in _get_contributor_role(contributor)
    ]


hakai_relations_to_zenodo_relations = {
    "largerWorkCitation": "isPartOf",
    "isComposedOf": "hasPart",
    "crossReference": "isReferencedBy",
    "dependency": "isRequiredBy",
}

hakai_authorities_to_zenodo_schemes = {
    "URL": "url",
    "DOI": "doi",
}


def _get_zenodo_relation(relation):
    if relation in hakai_relations_to_zenodo_relations:
        return hakai_relations_to_zenodo_relations[relation]
    if RAISE_ERRORS:
        raise ValueError(
            f"Relation {relation} not found in hakai_relations_to_zenodo_relations"
        )
    logger.warning(
        f"Relation {relation} not found in hakai_relations_to_zenodo_relations"
    )
    return "Other"


def _get_zenodo_scheme(authority):
    if authority in hakai_authorities_to_zenodo_schemes:
        return hakai_authorities_to_zenodo_schemes[authority]
    if RAISE_ERRORS:
        raise ValueError(
            f"Relation {relation} not found in hakai_relations_to_zenodo_relations"
        )
    logger.warning(
        f"Authority {authority} not found in hakai_authorities_to_zenodo_schemes"
    )
    return "Other"


def _get_related_identifiers(record):
    """Convert Hakai metadata related identifiers to Zenodo format."""
    logger.debug("Sort related identifiers")
    identifiers = [
        # {
        #     "identifier": record['metadata']['identifier'],
        #     "relation": "isMetadataFor",
        #     "resource_type": "publication",
        #     "scheme": 'crossref_funder_id', #TODO this failed with zenodo api
        # },
    ]
    if record["identification"].get("identifier"):
        # Add the DOI identifier
        identifiers.append(
            {
                "identifier": record["identification"]["identifier"].replace(
                    "https://doi.org/", ""
                ),
                "relation": "isMetadataFor",
                "resource_type": "publication",
                "scheme": "doi",
            }
        )
    for item in record["distribution"]:
        identifiers.append(
            {
                "identifier": item["url"],
                "relation": "isNewVersionOf",
                "resource_type": "dataset",
                "scheme": "url",
            }
        )
    for resource in record["identification"]["associated_resources"]:
        identifiers.append(
            {
                "identifier": resource["code"].replace("https://doi.org/", ""),
                "relation": _get_zenodo_relation(resource["association_type_iso"]),
                "resource_type": "other",
                "scheme": _get_zenodo_scheme(resource["authority"]),
            }
        )

    return identifiers


def _get_notes(record):
    """Convert Hakai metadata notes to Zenodo format."""
    notes = []
    if record["metadata"].get("maintenance_note"):
        notes.append(record["metadata"]["maintenance_note"])
    notes.append(
        "Metadata converted by "
        "<a href='https://github.com/HakaiInstitute/hakai-metadata-conversion'>hakai-metadata-conversion v{version} </a>"
    )
    return "<br><br>".join(notes)


def _get_dates(record):
    """Convert Hakai metadata dates to Zenodo format."""
    dates = []

    def _format_date(date):
        return date.split("T")[0] if date else None

    def _add_date(date_type, start=None, end=None, description=None):
        if not start and not end:
            return
        dates.append(
            {
                "start": _format_date(start),
                "end": _format_date(end),
                "type": date_type,
                "description": description,
            }
        )

    _add_date(
        "created",
        record["identification"].get("dates", {}).get("creation"),
        description="Date of dataset creation",
    )
    _add_date(
        "available",
        record["identification"].get("dates", {}).get("publication"),
        description="Date of dataset publication",
    )
    _add_date(
        "submitted",
        record["metadata"].get("dates", {}).get("publication"),
        description="Date of metadate publication",
    )
    _add_date(
        "updated",
        record["metadata"].get("dates", {}).get("revision"),
        description="Date of metadata revision",
    )
    _add_date(
        "collected",
        record["identification"].get("temporal_begin"),
        record["identification"].get("temporal_end"),
        description="Data Collection period",
    )
    return dates


def _get_licence(record):
    license = record["metadata"]["use_constraints"].get("licence", {}).get("code")
    if not license:
        logger.warning("No license found in metadata, defaulting to CC-BY-4.0")
        return "CC-BY-4.0"
    return license


def zenodo(record, language=None):
    """Convert Hakai metadata to Zenodo format."""
    if language is None:
        language = record["metadata"]["language"]

    return {
        "upload_type": "dataset",  # TODO Retrieve the right term in record
        "title": record["identification"]["title"][language],
        "creators": _get_creators(record),
        "contributors": _get_contributors(record),
        "description": record["identification"]["abstract"][language],
        # "access_right": record["access_right"],
        "license": _get_licence(record),
        # embargo_date": record["embargo_date"],
        # access_conditions": record["access_conditions"],
        # "doi": ignore this to generate a new DOI,
        # "preserve_doi": record["preserve_doi"],
        "related_identifiers": _get_related_identifiers(record),
        "keywords": record["identification"]["keywords"]["default"][language],
        "notes": _get_notes(record),
        # "references": record["references"],
        "dates": _get_dates(record),
        "version": record["identification"].get("edition", "v1"),
        "language": record["metadata"]["language"],
        # "locations": record["locations"],
    }
