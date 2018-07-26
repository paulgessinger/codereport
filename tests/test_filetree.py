from codereport.filetree import make_file_tree, SourceFile


def test_make_file_tree():
    files = ["./a/b/c/d.cpp", "./a/b/../b/c/e.cpp", "./a/./b/f.cpp", "./d.cpp"]

    tree = make_file_tree([SourceFile(f) for f in files])

    nodelist = list(tree.walk())

    for n in nodelist: print(n)

    tree.print()

    refs = [
        {"name": "a", "is_file": False, "nch": 2, "path": "a"},
        {"name": "b", "is_file": False, "nch": 2, "path": "a/b"},
        {"name": "c", "is_file": False, "nch": 2, "path": "a/b/c"},
        {"name": "d.cpp", "is_file": True, "nch": 0, "path": "a/b/c/d.cpp"},
        {"name": "e.cpp", "is_file": True, "nch": 0, "path": "a/b/c/e.cpp"},
        {"name": "f.cpp", "is_file": True, "nch": 0, "path": "a/b/f.cpp"},
        {"name": "d.cpp", "is_file": True, "nch": 0, "path": "a/d.cpp"},
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
