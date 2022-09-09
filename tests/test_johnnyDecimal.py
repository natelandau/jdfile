# type: ignore
"""Tests for the JohnnyDecimal utilities."""

from filemanager._utils.johnnyDecimal import JDFolder


def test_jdfolder_object(test_jd):
    """Tests the JDFolder class."""
    root = test_jd

    test_folder = JDFolder(str(root), "test_folder")

    assert test_folder.root == root
    assert test_folder.name == "test_folder"
