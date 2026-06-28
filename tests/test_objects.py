from io import BytesIO
from pathlib import Path

import pytest

from vcs.vcs_blob import VCSBlob
from vcs.vcs_commit import VCSCommit
from vcs.vcs_obj import object_find, object_hash, object_read, object_resolve, object_write
from vcs.vcs_repo import repo_create


def test_blob_hash_write_read_and_prefix_resolution(tmp_path: Path) -> None:
    repo = repo_create(str(tmp_path / "repo"))
    data = b"hello vcs\n"

    sha = object_hash(BytesIO(data), b"blob", repo)
    obj = object_read(repo, sha)

    assert isinstance(obj, VCSBlob)
    assert obj.serialize() == data
    assert object_resolve(repo, sha[:8]) == [sha]
    assert object_find(repo, sha[:8], fmt=b"blob") == sha


def test_ref_resolution_follows_head_to_branch(tmp_path: Path) -> None:
    repo = repo_create(str(tmp_path / "repo"))
    sha = object_hash(BytesIO(b"tracked content"), b"blob", repo)
    Path(repo.gitdir, "refs", "heads", "master").write_text(sha)

    assert object_resolve(repo, "HEAD") == [sha]
    assert object_resolve(repo, "master") == [sha]
    assert object_find(repo, "HEAD", fmt=b"blob") == sha


def test_object_find_can_follow_commit_to_tree(tmp_path: Path) -> None:
    repo = repo_create(str(tmp_path / "repo"))
    tree_sha = object_hash(BytesIO(b""), b"tree", repo)
    commit = VCSCommit()
    commit.kvlm = {
        b"tree": tree_sha.encode("ascii"),
        b"author": b"Alice <alice@example.com> 0 +0000",
        b"committer": b"Alice <alice@example.com> 0 +0000",
        None: b"initial commit\n",
    }
    commit_sha = object_write(commit, repo)
    Path(repo.gitdir, "refs", "heads", "master").write_text(commit_sha)

    assert object_find(repo, "master", fmt=b"commit") == commit_sha
    assert object_find(repo, "master", fmt=b"tree") == tree_sha
    with pytest.raises(Exception, match="expected type tree"):
        object_find(repo, "master", fmt=b"tree", follow=False)


def test_object_find_rejects_unknown_names(tmp_path: Path) -> None:
    repo = repo_create(str(tmp_path / "repo"))

    with pytest.raises(Exception, match="No such reference"):
        object_find(repo, "missing")
