import json
from glob import glob
from pathlib import Path

import click
import yaml
from loguru import logger

from hakai_metadata_conversion import citation_cff, erddap

output_formats = {
    "json": lambda x: json.dumps(x, indent=2),
    "yaml": lambda x: yaml.dump(x, default_flow_style=False),
    "erddap": erddap.dataset_xml,
    "cff": citation_cff.citation_cff,
}

input_formats = ["json", "yaml"]


def load(file, format, encoding="utf-8") -> dict:
    """Load a metadata record from a file."""

    if format == "json":
        with open(file) as f:
            return json.load(f, encoding=encoding)
    elif format == "yaml":
        with open(file) as f:
            return yaml.safe_load(f)

    with open(file) as f:
        return input_formats[format](f)


def convert(record, format) -> str:
    """Run the conversion to the desired format."""
    if format == "json":
        return json.dumps(record, indent=2)
    elif format == "yaml":
        return yaml.dump(record)
    elif format == "erddap":
        return erddap.dataset_xml(record)
    elif format == "cff":
        return citation_cff.citation_cff(record)
    else:
        raise ValueError(f"Unknown output format: {format}")


@click.command()
@click.option("--input", "-i", required=True, help="Input file.")
@click.option(
    "--recursive", "-r", is_flag=True, help="Process files recursively.", default=False
)
@click.option(
    "--input-file-format",
    required=True,
    default="yaml",
    help="Input file format (json or yaml).",
    type=click.Choice(list(input_formats)),
    show_default=True,
)
@click.option(
    "--encoding",
    default="utf-8",
    help="Encoding of the input file.",
    show_default=True,
)
@click.option(
    "--output-dir", "-p", type=click.Path(file_okay=False), help="Output directory, the original file name will be used."
)
@click.option(
    "--output-file", "-o", type=click.Path(), help="Output file"
)
@click.option(
    "--output-format",
    required=True,
    help="Output format",
    type=click.Choice(list(output_formats.keys())),
)
@click.option(
    "--output-encoding",
    default="utf-8",
    help="Encoding of the output file.",
    show_default=True,
)
@logger.catch(reraise=True)
def cli_main(**kwargs):
    """Convert metadata records to different metadata formats or standards."""
    main(**kwargs)


def main(
    input,
    recursive,
    input_file_format,
    encoding,
    output_dir,
    output_file,
    output_format,
    output_encoding,
):
    """Convert metadata records to different metadata formats or standards."""

    logger.info("Loading file {}", input)
    returned_output = ""
    files = glob(input, recursive=recursive)
    if len(files) > 1 and output_file:
        raise ValueError("Cannot specify output file when processing multiple files. Define an output directory instead.")
    
    for file in glob(input, recursive=recursive):
        input_file_path = Path(file)
        record = load(file, input_file_format, encoding=encoding)

        if not record:
            logger.error("No metadata record found.")
            return

        logger.info(f"Converting to {output_format}")
        converted_record = convert(record, output_format)

        if output_dir:
            output_file = (
                Path(output_dir) / input_file_path.with_suffix(f".{output_format}").name
            )

        if output_file:
            logger.info("Writing to file {}", output_dir)
            output_file.write_text(converted_record, encoding=output_encoding)
        else:
            returned_output += "\n" + converted_record

    return returned_output


if __name__ == "__main__":
    main()
