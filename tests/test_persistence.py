from tuneforge.persistence import directory_size_bytes, save_json


def test_directory_size_bytes(tmp_path):
    (tmp_path / "a.txt").write_text("abcd", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "b.txt").write_text("123456", encoding="utf-8")

    assert directory_size_bytes(tmp_path) == 10


def test_save_json(tmp_path):
    target = tmp_path / "out" / "metadata.json"
    save_json({"ok": True}, target)

    assert target.exists()
    assert '"ok": true' in target.read_text(encoding="utf-8")
