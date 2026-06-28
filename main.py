import click
import sys
from rich.console import Console
from rich.markup import escape
from rich.text import Text

from vcs.vcs_commit import log_graphviz
from vcs.vcs_console import ColorMode, console_for
from vcs.vcs_repo import repo_create, repo_find
from vcs.vcs_obj import object_find, object_hash, object_read


@click.group()
@click.option(
    "--color",
    "color_mode",
    type=click.Choice(["auto", "always", "never"]),
    default="auto",
    envvar="VCS_COLOR",
    show_default=True,
    help="Control colored output.",
)
@click.pass_context
def cli(ctx: click.Context, color_mode: ColorMode) -> None:
    """vcs: a mini git-like content tracker."""
    ctx.obj = {"color_mode": color_mode}


def get_console(ctx: click.Context) -> Console:
    color_mode: ColorMode = "auto"
    if isinstance(ctx.obj, dict):
        color_mode = ctx.obj.get("color_mode", "auto")
    return console_for(color_mode)


@cli.command("init")
@click.argument("path", default=".", metavar="directory")
@click.pass_context
def cmd_init(ctx: click.Context, path: str) -> None:
    """Initialize a new, empty repository."""
    repo = repo_create(path)
    console = get_console(ctx)
    message = Text("Initialized empty vcs repository in ")
    message.append(repo.gitdir, style="bold green")
    console.print(message)


@cli.command("cat-file")
@click.argument(
    "object_type", metavar="type", type=click.Choice(["blob", "commit", "tag", "tree"])
)
@click.argument("object_name", metavar="object")
def cmd_cat_file(object_type: str, object_name: str) -> None:
    """Provide content or type and size information for repository objects."""
    repo = repo_find()
    sha = object_find(repo, object_name, fmt=object_type.encode())
    read_obj = object_read(repo, sha)
    if read_obj is None:
        raise click.ClickException(f"Object {sha} not found")
    sys.stdout.buffer.write(read_obj.serialize())


@cli.command("hash-object")
@click.option(
    "-t",
    "--type",
    "object_type",
    default="blob",
    type=click.Choice(["blob", "commit", "tag", "tree"]),
    help="Specify the type.",
)
@click.option(
    "-w", "--write", is_flag=True, help="Actually write the object into the database."
)
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def cmd_hash_object(
    ctx: click.Context, object_type: str, write: bool, path: str
) -> None:
    """Compute object ID and optionally creates a blob from a file."""
    if write:
        repo = repo_find()
    else:
        repo = None

    with open(path, "rb") as fd:
        sha = object_hash(fd, object_type.encode(), repo)
        get_console(ctx).print(escape(sha), style="bold yellow")


@cli.command("log", help="Display history of a given commit.")
@click.argument("commit", default="HEAD", required=False)
def cmd_log(commit: str) -> None:
    """Show the commit log."""
    repo = repo_find()

    print("digraph vcs{")
    print("  node[shape=rect]")
    log_graphviz(repo, object_find(repo, commit, fmt=b"commit"), set())
    print("}")


@cli.command("ls-tree")
@click.option("-r", "recursive", is_flag=True, help="Recurse into sub-trees.")
@click.argument("tree")
def cmd_ls_tree(recursive: bool, tree: str) -> None:
    """List the contents of a tree object."""
    pass


@cli.command("checkout")
@click.argument("commit")
@click.argument("path")
def cmd_checkout(commit: str, path: str) -> None:
    """Checkout a branch or paths to the working tree."""
    pass


@cli.command("show-ref")
def cmd_show_ref() -> None:
    """List references in a local repository."""
    pass


@cli.command("tag")
@click.option(
    "-a", "create_tag_object", is_flag=True, help="Whether to create a tag object."
)
@click.argument("name", required=False)
@click.argument("object_name", metavar="object", default="HEAD", required=False)
def cmd_tag(create_tag_object: bool, name: str | None, object_name: str) -> None:
    """Create, list, delete or verify a tag object signed with GPG."""
    pass


@cli.command("rev-parse")
@click.option(
    "--vcs-type",
    "object_type",
    default=None,
    type=click.Choice(["blob", "commit", "tag", "tree"]),
    help="Specify the expected type.",
)
@click.argument("name")
def cmd_rev_parse(object_type: str | None, name: str) -> None:
    """Pick out and massage parameters."""
    pass


@cli.command("ls-files")
@click.option("--verbose", is_flag=True, help="Show everything.")
def cmd_ls_files(verbose: bool) -> None:
    """Show information about files in the index and the working tree."""
    pass


@cli.command("check-ignore")
@click.argument("path", nargs=-1, required=True)
def cmd_check_ignore(path: tuple[str, ...]) -> None:
    """Check path(s) against ignore rules."""
    pass


@cli.command("status")
def cmd_status() -> None:
    """Show the working tree status."""
    pass


@cli.command("add")
def cmd_add() -> None:
    """Add file contents to the index."""
    pass


@cli.command("rm")
def cmd_rm() -> None:
    """Remove files from the working tree and from the index."""
    pass


@cli.command("commit")
def cmd_commit() -> None:
    """Record changes to the repository."""
    pass


if __name__ == "__main__":
    cli()
