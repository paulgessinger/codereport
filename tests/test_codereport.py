from codereport import CodeReport
from codereport.codereport import TreeNode
from unittest.mock import Mock, call, patch

def test_make_file_tree():

    files = ["a/b/c/d.cpp", "a/b/c/e.cpp", "a/b/f.cpp", "d.cpp"]
    cr = CodeReport(files, Mock())

    tree = cr._make_file_tree()
    print(tree)

    assert type(tree) == list
    assert len(tree) == 1

    root = tree[0]

    assert type(root) == TreeNode
    assert len(root.files) == 1
    assert len(root.subdirs) == 1
    fname, _ = root.files[0]
    assert fname == "d.cpp"

    dir_a = root.subdirs[0]
    assert type(dir_a) == TreeNode
    assert dir_a.name == "a"
    assert len(dir_a.subdirs) == 1
    assert len(dir_a.files) == 0

    dir_b = dir_a.subdirs[0]
    assert type(dir_b) == TreeNode
    assert dir_b.name == "b"
    assert len(dir_b.subdirs) == 1
    assert len(dir_b.files) == 1
    fname, _ = dir_b.files[0]
    assert fname == "f.cpp"

    dir_c = dir_b.subdirs[0]
    assert type(dir_c) == TreeNode
    assert len(dir_c.subdirs) == 0
    assert len(dir_c.files) == 2

    fname1, _ = dir_c.files[0]
    fname2, _ = dir_c.files[1]

    assert fname1 == "d.cpp"
    assert fname2 == "e.cpp"
