from codereport.filetree import make_file_tree, SourceFile

ROOT_MARKER = "<root-marker>"

def test_make_file_tree():
    files = ["./a/b/c/d.cpp", "./a/b/../b/c/e.cpp", "./a/./b/f.cpp", "./d.cpp"]

    tree = make_file_tree([SourceFile(f) for f in files], root_name=ROOT_MARKER)

    nodelist = list(tree.walk())

    for n in nodelist: print(n)

    tree.print()

    refs = [
        {"name": ROOT_MARKER, "is_file": False, "nch": 2, "path": ""},
        {"name": "a", "is_file": False, "nch": 1, "path": "a"},
        {"name": "b", "is_file": False, "nch": 2, "path": "a/b"},
        {"name": "c", "is_file": False, "nch": 2, "path": "a/b/c"},
        {"name": "d.cpp", "is_file": True, "nch": 0, "path": "a/b/c/d.cpp"},
        {"name": "e.cpp", "is_file": True, "nch": 0, "path": "a/b/c/e.cpp"},
        {"name": "f.cpp", "is_file": True, "nch": 0, "path": "a/b/f.cpp"},
        {"name": "d.cpp", "is_file": True, "nch": 0, "path": "d.cpp"},
    ]

    assert len(nodelist) == len(refs)

    for idx, node in enumerate(nodelist):
        ref = refs[idx]
        assert node.name == ref["name"]
        assert node.is_file == ref["is_file"]
        assert len(list(node.children)) == ref["nch"]
        assert node.path == ref["path"]

def test_make_file_tree_multiple_root_dirs():
    files = ["./a/file1.cpp", "./b/file2.cpp", "./c/file3.cpp", "./c/file4.cpp", "./file5.cpp"]

    tree = make_file_tree([SourceFile(f) for f in files], root_name=ROOT_MARKER)
    tree.print()

    nodelist = list(tree.walk())
    for n in nodelist: print(n)

    refs = [
        {"name": ROOT_MARKER, "is_file": False, "nch": 4, "path": ""},
        {"name": "a", "is_file": False, "nch": 1, "path": "a"},
        {"name": "file1.cpp", "is_file": True, "nch": 0, "path": "a/file1.cpp"},
        {"name": "b", "is_file": False, "nch": 1, "path": "b"},
        {"name": "file2.cpp", "is_file": True, "nch": 0, "path": "b/file2.cpp"},
        {"name": "c", "is_file": False, "nch": 2, "path": "c"},
        {"name": "file3.cpp", "is_file": True, "nch": 0, "path": "c/file3.cpp"},
        {"name": "file4.cpp", "is_file": True, "nch": 0, "path": "c/file4.cpp"},
        {"name": "file5.cpp", "is_file": True, "nch": 0, "path": "file5.cpp"},
    ]

    assert len(nodelist) == len(refs)

    for idx, node in enumerate(nodelist):
        ref = refs[idx]
        assert node.name == ref["name"]
        assert node.is_file == ref["is_file"]
        assert len(list(node.children)) == ref["nch"]
        assert node.path == ref["path"]

def test_sourcefile():
    f = "a/b/c.cpp"
    sf = SourceFile(f)
    assert sf.report_file_name == "a_b_c.cpp.html"
