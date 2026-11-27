# CIOOS Metadata Conversion

This project provides a tool to generate various metadata formats and standards
from the CIOOS metadata catalogue form schema. It aims to
facilitate the sharing and citation of datasets by converting metadata records into
widely recognized standards.

## Currently Supported Standards

- `citation.cff`: Citation File Format, a human and machine-readable file format
  which provides citation metadata for software.
- `ACDD-1.3`: ACDD-1.3 standard attributes.
- ERDDAP<sup>TM</sup>: XML metadata attributes following the CF1.6 and ACDD 1.3 standards.
- `ISO19115-3` schema: CIOOS standard ISO19115-3 schema.
- `Datacite-xml` and `Datacite-json` schema: Datacite compatible Schema.

## Features

- **Easy Integration**: Seamlessly integrates with existing CKAN instances to
  fetch catalogue records.
- **Extensible**: Designed with extensibility in mind, allowing for adding more metadata standards in the future.
- **User-Friendly**: Provides a simple, intuitive interface for generating
  metadata files.

## Getting Started

To use this tool, follow these steps to install it as a modul:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your/repository.git
   cd repository
   ```

2. **Install Dependencies:**

    ```bash
    uv sync
    ```

3. **Run the Tool:**

    ```bash
    uv run hakai_metadata_conversion 
    ```

   For more information

    ```bash
    uv run hakai_metadata_conversion --help
    ```

## Install cli
```
uv tool install . -e
```

## Run Cli
```
hakai_metadata_conversion --help
```

## Use within an action

The tool can be use within a github action by adding the following step within your action:

```yaml
job: 
    sync:
        step:
            - use: action/checkout@v4
            - name: Sync metadata
              use: hakaiinstitute/hakai-metadata-conversion
              with:
                - input: url or file path within repo
                - output-file: CITATION.cff
                - output-format: cff
```

## Environment Variables

Copy `.env.sample` to `.env` and fill in the values:

| Variable | Description |
|---|---|
| `LOCAL_RECORDS_PATH` | Path to local metadata records |
| `DATACITE_ACCOUNT_ID` | DataCite repository ID for API access |
| `DATACITE_PASSWORD` | DataCite repository password |
| `DATACITE_PREFIX` | DataCite DOI prefix (e.g. `10.xxxxx`) |

The DataCite credentials are used by integration tests to submit records to the
[DataCite test API](https://api.test.datacite.org). You can obtain test
credentials at <https://doi.test.datacite.org/>.

## Testing
To test the core application
```
cd tests/records
git clone https://github.com/HakaiInstitute/hakai-metadata-entry-form-files.git
cd ../..
uv sync --dev
uv run pytest -m core
```

To test that converting all yaml files from the metadata files repo have been marked as 'metadataFiles'. These test take a long time so you might want the exitfirst flag which will stop after the first fail.
```
uv run pytest --exitfirst -m metadataFiles
```

To test it all
```
uv run pytest
```

## Liniting
```
uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude .venv
uv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude .venv
```

## How to Contribute

We welcome contributions! If you would like to add support for more metadata standards or improve the tool, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature (git checkout -b feature/AmazingFeature).
3. Commit your changes (git commit -m 'Add some AmazingFeature').
4. Push to the branch (git push origin feature/AmazingFeature).
5. Open a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
