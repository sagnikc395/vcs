import os
from pathlib import Path

from click.utils import strip_ansi
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

        colored_cat_result = runner.invoke(
            cli, ["--color", "always", "cat-file", "blob", sha], color=True
        )
        assert colored_cat_result.exit_code == 0
        assert colored_cat_result.stdout_bytes == b"from the cli\n"


def test_cli_hash_object_can_force_colored_output(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("sample.txt").write_text("color me\n")

        result = runner.invoke(
            cli, ["--color", "always", "hash-object", "sample.txt"], color=True
        )

        assert result.exit_code == 0
        assert "\x1b[" in result.output
        assert strip_ansi(result.output).strip()


def test_cli_hash_object_auto_color_stays_plain_when_captured(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("sample.txt").write_text("plain\n")

        result = runner.invoke(cli, ["hash-object", "sample.txt"])

        assert result.exit_code == 0
        assert "\x1b[" not in result.output
        assert len(result.output.strip()) == 40
