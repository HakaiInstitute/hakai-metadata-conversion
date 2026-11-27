from glob import glob
from pathlib import Path

import pytest
from click.testing import CliRunner

from hakai_metadata_conversion.__main__ import cli


@pytest.fixture
def runner():
    return CliRunner(echo_stdin=False, catch_exceptions=True)

@pytest.mark.skip(reason="cli without args dosn't work from tests. not sure why")
def test_cli_no_args(runner):
    result = runner.invoke(cli)
    assert result.exit_code == 2, result.output
    assert "Usage: cioos-metadata-conversion [OPTIONS] COMMAND [ARGS]" in result.output

@pytest.mark.core
def test_cli_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage: cioos-metadata-conversion [OPTIONS]" in result.output

@pytest.mark.core
def test_cli_glob_writes_one_output_per_input(runner, tmp_path):
    """A glob matching several records must leave one output per record.

    test_cli_on_test_files below looks like it covers this, but
    tests/records/*.yaml matches a single file, so the multi-file path went
    untested - and was broken: the destination was computed once into the same
    variable the loop tested, so every record after the first overwrote the
    first record's file and only the last survived.
    """
    source = Path("tests/records/test_record1.yaml").read_text(encoding="utf-8")
    inputs = tmp_path / "in"
    outputs = tmp_path / "out"
    inputs.mkdir()
    outputs.mkdir()
    for name in ("rec_a", "rec_b", "rec_c"):
        (inputs / f"{name}.yaml").write_text(source, encoding="utf-8")

    result = runner.invoke(
        cli,
        [
            "convert",
            "--input",
            str(inputs / "*.yaml"),
            "--input-schema",
            "CIOOS",
            "--output-format",
            "cff",
            "--output-dir",
            str(outputs),
        ],
    )
    assert result.exit_code == 0, result.output
    assert sorted(p.name for p in outputs.iterdir()) == [
        "rec_a.cff",
        "rec_b.cff",
        "rec_c.cff",
    ]


@pytest.mark.core
def test_cli_single_output_file_still_honoured(runner, tmp_path):
    """--output-file keeps overriding --output-dir for a single input."""
    destination = tmp_path / "CITATION.cff"
    result = runner.invoke(
        cli,
        [
            "convert",
            "--input",
            "tests/records/test_record1.yaml",
            "--input-schema",
            "CIOOS",
            "--output-format",
            "cff",
            "--output-file",
            str(destination),
        ],
    )
    assert result.exit_code == 0, result.output
    assert destination.is_file()
    assert destination.read_text(encoding="utf-8").strip()


@pytest.mark.core
def test_cli_on_test_files(runner, tmpdir):
    input_files = "tests/records/*.yaml"
    n_test_files = len(glob(input_files))
    args = [
        "convert",
        "--input",
        input_files,
        "--input-schema",
        "CIOOS",
        "--output-format",
        "cff",
        "--output-dir",
        str(tmpdir),
    ]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.output
    assert result.output == ""
    assert len(tmpdir.listdir()) == n_test_files

@pytest.mark.core
def test_cli_output_file(runner, tmpdir):
    args = [
        "convert",
        "--input",
        "tests/records/*.yaml",
        "--input-schema",
        "CIOOS",
        "--output-format",
        "cff",
        "--output-file",
        str(tmpdir / "CITATION.cff"),
    ]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert result.output == ""
    assert len(tmpdir.listdir()) == 1
    assert tmpdir.join("CITATION.cff").check(file=True)
    assert "cff-version: 1.2.0" in tmpdir.join("CITATION.cff").read_text(
        encoding="UTF-8"
    )

@pytest.mark.core
def test_cli_with_http_input(runner, tmpdir):
    ouput_file = "CITATION.cff"
    args = [
        "convert",
        "--input",
        "https://raw.githubusercontent.com/hakaiinstitute/hakai-metadata-conversion/main/tests/records/test_record1.yaml",
        "--input-schema",
        "CIOOS",
        "--output-format",
        "cff",
        "--output-file",
        str(tmpdir / ouput_file),
    ]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.output
    assert result.output == ""
    assert len(tmpdir.listdir()) == 1
    assert tmpdir.join(ouput_file).check(file=True)
    assert "cff-version: 1.2.0" in tmpdir.join(ouput_file).read_text(encoding="UTF-8")
