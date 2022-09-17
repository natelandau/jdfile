# type: ignore
"""Test utility helpers."""
from io import StringIO

from filemanager._utils.utilities import dedupe_list, diff_strings, select_option


def test_dedupe_list():
    """Test dedupe lists."""
    original = ["a", "b", "c", "a", "b", "c"]
    expected = ["a", "b", "c"]
    assert sorted(dedupe_list(original)) == sorted(expected)


def test_diff_strings():
    """Test diffing strings."""
    a = "abc"
    b = "bcd"
    expected = "[red reverse]a[/]bc[green reverse]d[/]"
    assert diff_strings(a, b) == expected

    a = "quick brown fox"
    b = "quick Red Fox"
    expected = (
        "quick [green reverse]Red[/][red reverse]brown[/] [green reverse]F[/][red reverse]f[/]ox"
    )
    assert diff_strings(a, b) == expected


def test_select_option(monkeypatch, capsys):
    """Test selecting an option."""
    options = {"a": "Select a", "b": "Select B", "c": "Select C"}

    monkeypatch.setattr("sys.stdin", StringIO("a"))
    assert select_option(options) == "a"
    captured = capsys.readouterr()
    assert captured.out == "Select an option: "

    monkeypatch.setattr("sys.stdin", StringIO("A"))
    assert select_option(options, prompt="choose") == "A"
    captured = capsys.readouterr()
    assert captured.out == "choose: "

    monkeypatch.setattr("sys.stdin", StringIO("A"))
    assert select_option(options, show_choices=True) == "A"
    captured = capsys.readouterr()
    assert "Options:\n" in captured.out
    assert " A  Select a\n" in captured.out
    assert " B  Select B\n" in captured.out
    assert " C  Select C\n" in captured.out

    monkeypatch.setattr("sys.stdin", StringIO("N\nA"))
    assert select_option(options, show_choices=True) == "A"
    captured = capsys.readouterr()
    assert "Invalid option: N\n" in captured.out

    monkeypatch.setattr("sys.stdin", StringIO("N\nX\nA"))
    assert select_option(options, same_line=True) == "A"
    captured = capsys.readouterr()
    assert "Invalid option: N\n" in captured.out
    assert "Invalid option: X\n" in captured.out
