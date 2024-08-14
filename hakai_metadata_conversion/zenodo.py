def _get_creator(creator):
        return {
            "name": creator.get("individual",{}).get('name'),
            "affiliation": creator.get("organization",{}).get('name'),
            "orcid": creator.get("individual",{}).get('orcid'),
            # "gnd": creator.get("gnd")
        }

def _get_creators(record):
    """Convert Hakai metadata creators to Zenodo format."""
    return [
        _get_creator(creator) for creator in record["contact"] if creator['inCitation']
    ]

def _get_contributors(record):
    """Convert Hakai metadata contributors to Zenodo format."""
    return [
         _get_creator(contributor) for contributor in record["contact"]
    ]

def _get_related_identifiers(record):
    """Convert Hakai metadata related identifiers to Zenodo format."""
    if "identifier" not in record["identification"]:
        return []
    return [
        {
            "identifier": record["identification"]["identifier"],
            "relation": "isMetadataFor",
            "resource_type": "publication_type",
        },
    ]

def zenodo(record, language=None):
    """Convert Hakai metadata to Zenodo format."""
    if language is None:
        language = record['metadata']['language']
        
    return {
        "upload_type": 'dataset', #TODO Retrieve the right term in record
        "title": record["identification"]["title"],
        "creators": _get_creators(record),
        "description": record["identification"]["abstract"][language],   
        # "access_right": record["access_right"],
        "license": record["metadata"]["use_constraints"]['licence']['code'],
        # embargo_date": record["embargo_date"],
        # access_conditions": record["access_conditions"],
        # "doi": record["doi"],
        # "preserve_doi": record["preserve_doi"],
        "keywords": record["identification"]["keywords"]['default'][language],
        "notes": record["metadata"].get('history'),
        "related_identifiers":  _get_related_identifiers(record),
        "contributors": _get_contributors(record),
        # "references": record["references"],
        "version": record["identification"].get('edition'),
        "language": record['metadata']['language'],
        # "locations": record["locations"],
    }