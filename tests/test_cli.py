from pathlib import Path

from click.testing import CliRunner
import pytest

from clea.__main__ import main


TESTS_DIRECTORY = Path(__file__).parent


@pytest.mark.parametrize("xml_file_path", TESTS_DIRECTORY.glob("xml/*"))
def test_clea_cli_from_valid_files(xml_file_path, monkeypatch):
    xml_file_name = str(xml_file_path.relative_to(TESTS_DIRECTORY))
    json_file_path = TESTS_DIRECTORY / f"json/{xml_file_path.stem}.json"
    with open(json_file_path, "rb") as json_file:
        expected_result = json_file.read()

    monkeypatch.chdir(TESTS_DIRECTORY)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(main, [xml_file_name])

    assert result.exit_code == 0
    assert result.stdout_bytes == expected_result
    assert result.stderr_bytes == b""
