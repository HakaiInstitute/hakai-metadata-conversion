from loguru import logger
from hakai_metadata_conversion.__version__ import version
def _get_creator(creator):
        if creator.get("individual",{}).get('name'):
            return _get_person(creator)
        return _get_organization(creator)

def _get_organization(organization):
    return {
        "name": organization.get("organization",{}).get('name'),
        "ror": organization.get("organization",{}).get('ror'),
        "affiliation": organization.get("organization",{}).get('name'),
    }

def _get_person(person):
     return {
        "name": person.get("individual",{}).get('name'),
        "affiliation": person.get("organization",{}).get('name'),
        "orcid": person.get("individual",{}).get('orcid'),
        # "gnd": person.get("gnd")
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
    logger.debug("Sort related identifiers")
    identifiers = [
        # {
        #     "identifier": record['metadata']['identifier'],
        #     "relation": "isMetadataFor",
        #     "ressource_type": "publication_type",
        #     "scheme": 'crossRefFunderID',
        # },
    ] 
    if record['identification'].get('identifier'):
        # Add the DOI identifier
        identifiers.append(
            {
                "identifier": record['identification']['identifier'].replace("https://doi.org/",""),
                "relation": "isMetadataFor",
                "ressource_type": "dataset",
                "scheme": 'doi', #TODO Retrieve the right term in record 
            }
        )
    for item in record['distribution']:
         identifiers.append(
              {
                "identifier": item['url'],
                "relation": "isNewVersionOf",
                "ressource_type": "dataset",
                "scheme": 'url',
              }
         )
    
    #TODO missing related works section which I'm not sure belongs here
    return identifiers

def zenodo(record, language=None):
    """Convert Hakai metadata to Zenodo format."""
    if language is None:
        language = record['metadata']['language']
        
    return {
        "upload_type": 'dataset', #TODO Retrieve the right term in record
        "title": record["identification"]["title"][language],
        "creators": _get_creators(record),
        "description": record["identification"]["abstract"][language],   
        # "access_right": record["access_right"],
        "license": record["metadata"]["use_constraints"].get('licence',{}).get('code'),
        # embargo_date": record["embargo_date"],
        # access_conditions": record["access_conditions"],
        # "doi": record["doi"],
        # "preserve_doi": record["preserve_doi"],
        "keywords": record["identification"]["keywords"]['default'][language],
        "notes": record["metadata"].get('maintenance_note','') + '\n\n' + f"Converted by hakai-metadata-conversion v{version}",
        "related_identifiers":  _get_related_identifiers(record),
        "contributors": _get_contributors(record),
        # "references": record["references"],
        "version": record["identification"].get('edition'),
        "language": record['metadata']['language'],
        # "locations": record["locations"],
    }