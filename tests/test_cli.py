import os
from pathlib import Path

from click.testing import CliRunner

from main import cli


def test_cli_can_write_and_read_blob(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        init_result = runner.invoke(cli, ["init", "repo"])
        assert init_result.exit_code == 0

        os.chdir("repo")
        Path("sample.txt").write_bytes(b"from the cli\n")

        hash_result = runner.invoke(cli, ["hash-object", "-w", "sample.txt"])
        assert hash_result.exit_code == 0
        sha = hash_result.output.strip()

        cat_result = runner.invoke(cli, ["cat-file", "blob", sha])
        assert cat_result.exit_code == 0
        assert cat_result.stdout_bytes == b"from the cli\n"
