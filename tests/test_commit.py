import pytest

from vcs.vcs_commit import kvlm_parse, kvlm_serialize


def test_kvlm_parse_round_trips_repeated_keys_and_continuations() -> None:
    raw = (
        b"tree 0123456789abcdef0123456789abcdef01234567\n"
        b"parent 1111111111111111111111111111111111111111\n"
        b"parent 2222222222222222222222222222222222222222\n"
        b"author Alice <alice@example.com> 0 +0000\n"
        b"gpgsig -----BEGIN SIGNATURE-----\n"
        b" line two\n"
        b"\n"
        b"subject\n\nbody\n"
    )

    kvlm = kvlm_parse(raw)

    assert kvlm[b"tree"] == b"0123456789abcdef0123456789abcdef01234567"
    assert kvlm[b"parent"] == [
        b"1111111111111111111111111111111111111111",
        b"2222222222222222222222222222222222222222",
    ]
    assert kvlm[b"gpgsig"] == b"-----BEGIN SIGNATURE-----\nline two"
    assert kvlm[None] == b"subject\n\nbody\n"
    assert kvlm_serialize(kvlm) == raw


def test_kvlm_parse_rejects_header_without_message_separator() -> None:
    with pytest.raises(Exception, match="missing message separator"):
        kvlm_parse(b"tree")


def test_kvlm_serialize_rejects_multiple_messages() -> None:
    with pytest.raises(Exception, match="message cannot have multiple values"):
        kvlm_serialize({None: [b"one", b"two"]})
