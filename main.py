
import click
import sys 

from vcs.vcs_repo import repo_create, repo_find
from vcs.vcs_obj import object_read,object_find


@click.group()
def cli():
    """A mini git-like VCS."""
    pass


@cli.command("init")
@click.argument("path", default=".", metavar="directory")
def init(path):
    """Initialize a new, empty repository."""
    repo_create(path)


@cli.command("cat-file")
@click.argument("type", type=click.Choice(["blob", "commit", "tag", "tree"]),help="Specify the type")
@click.argument("object",help="The object to display")
def cat_file(type, object):
    """Provide content or type and size information for repository objects."""
    repo = repo_find()
    read_obj = object_read(repo,object_find(repo,object,fmt=type.encode()))
    sys.stdout.buffer.write(read_obj.serialize())
    


@cli.command("hash-object")
@click.option(
    "-t",
    "type",
    default="blob",
    type=click.Choice(["blob", "commit", "tag", "tree"]),
    help="Specify the type.",
)
@click.option(
    "-w", "write", is_flag=True, help="Actually write the object into the database."
)
@click.argument("path",help="Read object from <file>")
def hash_object(type, write, path):
    """Compute object ID and optionally creates a blob from a file."""
    pass


@cli.command()
@click.argument("commit", default="HEAD")
def log(commit):
    """Show the commit log."""
    pass


@cli.command("ls-tree")
@click.option("-r", "recursive", is_flag=True, help="Recurse into sub-trees.")
@click.argument("tree")
def ls_tree(recursive, tree):
    """List the contents of a tree object."""
    pass


@cli.command()
@click.argument("commit")
@click.argument("path")
def checkout(commit, path):
    """Checkout a branch or paths to the working tree."""
    pass


@cli.command("show-ref")
def show_ref():
    """List references in a local repository."""
    pass


@cli.command()
@click.option(
    "-a", "create_tag_object", is_flag=True, help="Whether to create a tag object."
)
@click.argument("name", required=False)
@click.argument("object", default="HEAD", required=False)
def tag(create_tag_object, name, object):
    """Create, list, delete or verify a tag object signed with GPG."""
    pass


@cli.command("rev-parse")
@click.option(
    "--vcs-type",
    "type",
    default=None,
    type=click.Choice(["blob", "commit", "tag", "tree"]),
    help="Specify the expected type.",
)
@click.argument("name")
def rev_parse(type, name):
    """Pick out and massage parameters."""
    pass


@cli.command("ls-files")
@click.option("--verbose", is_flag=True, help="Show everything.")
def ls_files(verbose):
    """Show information about files in the index and the working tree."""
    pass


@cli.command("check-ignore")
@click.argument("path", nargs=-1, required=True)
def check_ignore(path):
    """Check path(s) against ignore rules."""
    pass


@cli.command()
def status():
    """Show the working tree status."""
    pass


@cli.command()
def add():
    """Add file contents to the index."""
    pass


@cli.command()
def rm():
    """Remove files from the working tree and from the index."""
    pass


@cli.command()
def commit():
    """Record changes to the repository."""
    pass


def main():
    cli()
