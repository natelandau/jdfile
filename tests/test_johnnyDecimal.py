# type: ignore
"""Tests for the JohnnyDecimal utilities."""

from filemanager._utils.johnnyDecimal import JDProject


def test_jdproject_object(test_jd):
    """Tests the JDProject class."""
    root = test_jd

    test_folder = JDProject(str(root), "test_folder")

    assert test_folder.root == root
    assert test_folder.name == "test_folder"
