import os

class TreeNode:
    def __init__(self, name, raw_path="", parent=None):
        self.name = name
        self.parent = parent
        self.files = []
        self.subdirs = {}
        self.raw_path = raw_path

    def attach(self, path, raw_path):
        # print("attach", self.name, path)
        parts = path.split("/", 1)
        if len(parts) == 1:
            # print(" => file")
            self.files.append(TreeNode(parts[0], raw_path, parent=self))
        else:
            # print(" => dir")
            node, other = parts
            if not node in self.subdirs:
                self.subdirs[node] = TreeNode(node, parent=self)
            self.subdirs[node].attach(other, raw_path)

    @property
    def children(self):
        for _, v in self.subdirs.items():
            yield v
        for f in self.files:
            yield f

    @property
    def is_file(self):
        return len(self.files) == 0 and len(self.subdirs) == 0

    @property
    def is_dir(self):
        return not self.is_file

    @property
    def path(self):
        if self.parent is not None:
            return os.path.join(self.parent.path, self.name)
        else:
            return self.name

    def __repr__(self):
        tp = "File" if self.is_file else "Dir"
        p = (tp, self.name, self.path, self.raw_path)
        return '%sNode(name="%s", path="%s", raw_path="%s")' % p

    def walk(self):
        # if self.parent == None:
        yield self
        for _, d in self.subdirs.items():
            for df in d.walk():
                yield df
        for f in self.files:
            yield f

    def print(self, prefix=""):
        print(prefix+"-"+self.name)
        for _, d in self.subdirs.items():
            d.print(prefix+" |")
        for f in self.files:
            f.print(prefix+" |")
        if not self.is_file:
            print(prefix)

def make_file_tree(files):
    def trf(f):
        return os.path.normpath(f), f

    files = list(sorted(map(trf, files)))

    root_name, _ = files[0][0].split("/", 1)
    root = TreeNode(root_name)

    for f, rpath in files:
        print(f, rpath)
        parts = f.split("/", 1)
        if len(parts) == 1:
            root.attach(parts[0], rpath)
        else:
            node, other = parts
            root.attach(other, rpath)
    return root
