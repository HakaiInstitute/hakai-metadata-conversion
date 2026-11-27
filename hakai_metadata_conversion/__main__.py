
# Convert one metadata format into another.

# Example Usage:

# cd hakai-metadata-entry-form-files/hakai
# find *.yaml -maxdepth 1 -type f -exec \
#     hakai_metadata_conversion convert \
#     --input {} \
#     --input-file-format yaml \
#     --encoding utf-8 \
#     --output-format erddap \
#     --output-encoding utf-8 \;


from glob import glob
from pathlib import Path

import click
from loguru import logger

from hakai_metadata_conversion import erddap
from hakai_metadata_conversion.record import OUTPUT_FORMATS, InputSchemas, Record


def load(file: str, schema: str = "CIOOS"):
    """Load a metadata record from a file or URL."""
    record = (
        Record(source=file, schema=InputSchemas[schema])
        .load()
        .convert_to_cioos_schema()
    )

    if not record.metadata:
        raise ValueError(f"No metadata record found in file {file}.")

    return record.metadata


@click.group(name="cioos-metadata-conversion")
def cli():
    """CIOOS Metadata Conversion CLI.
    Convert metadata records to different metadata formats or standards.
    """
    pass


cli.add_command(erddap.update, name="erddap-update")


@cli.command(name="convert")
@click.option("--input", "-i", required=True, help="Input file.")
@click.option(
    "--recursive", "-r", is_flag=True, help="Process files recursively.", default=False
)
@click.option(
    "--input-schema",
    required=True,
    default="CIOOS",
    help="Input file format (json or yaml).",
    type=click.Choice(InputSchemas.__members__.keys()),
    show_default=True,
)
@click.option(
    "--encoding",
    default="utf-8",
    help="Encoding of the input file.",
    show_default=True,
)
@click.option(
    "--output-dir",
    "-p",
    type=click.Path(file_okay=False),
    help="Output directory, the original file name will be used.",
    default=".",
    show_default=True,
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(),
    help="Output file, this will override the output directory and is only valid for a single input file.",
)
@click.option(
    "--output-format",
    "-f",
    required=True,
    help="Output format",
    type=click.Choice(OUTPUT_FORMATS.keys()),
)
@click.option(
    "--output-encoding",
    default="utf-8",
    help="Encoding of the output file.",
    show_default=True,
)
@logger.catch(reraise=True)
def cli_convert(**kwargs):
    """Convert metadata records to different metadata formats or standards."""
    convert(**kwargs)


@logger.catch(reraise=True)
def convert(
    input,
    output_format: str,
    recursive: bool = False,
    input_schema: str = "CIOOS",
    encoding: str = "utf-8",
    output_dir: str = ".",
    output_file: str = None,
    output_encoding: str = "utf-8",
):
    """Convert metadata records to different metadata formats or standards."""

    logger.info("Loading input {}", input)
    if (
        input.startswith(("http", "10.", "doi:", "DOI:"))
        or input.isdigit()
        or input_schema in ["doi", "obis"]
    ):
        # URLs, DOIs, PDC CCIN reference numbers, and OBIS/DOI schemas are
        # passed through as-is
        files = [input]
    else:
        files = glob(input, recursive=recursive)

    if len(files) > 1 and output_file:
        raise ValueError(
            "Cannot specify output file when processing multiple files. Define an output directory instead."
        )

    logger.debug("Processing {} files", len(files))
    returned_output = ""
    # Held separately from the per-file destination below. This used to be the
    # `output_file` variable itself, reassigned inside the loop: the first file
    # set it, and every file after that took the `elif` branch and wrote over
    # the same path, so converting a glob left only the last record on disk.
    explicit_output = Path(output_file) if output_file else None
    wrote_any = False
    for file in files:
        logger.debug("Processing file {}", file)
        record = (
            Record(
                source=file,
                schema=InputSchemas[input_schema],
            )
            .load(encoding=encoding)
            .convert_to_cioos_schema()
        )

        if not record.metadata:
            logger.error("No metadata record found in file {}.", file)
            continue

        logger.debug(f"Converting to {output_format}")
        converted_record = record.convert_to(output_format)

        # Generate output file path, fresh for each input
        destination = explicit_output
        if destination is None and output_dir and record.source_is_path():
            destination = (
                Path(output_dir) / Path(file).with_suffix(f".{output_format}").name
            )

        # Write to file or return output
        if destination:
            logger.info("Writing to file {}", destination)
            destination.write_text(converted_record, encoding=output_encoding)
            wrote_any = True
        else:
            returned_output += "\n" + converted_record

    if wrote_any:
        logger.info("Conversion completed.")
    else:
        logger.info("Returning converted output")
        print(returned_output)

    return returned_output


if __name__ == "__main__":
    cli()
