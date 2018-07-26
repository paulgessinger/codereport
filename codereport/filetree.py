import os

def psplit(p):
    if p.startswith("/"):
        node, other = p[1:].split("/", 1)
        return node, other
    else:
        return p.split("/", 1)

class TreeNode:
    def __init__(self, parent=None):
        self.parent = parent
        self.files = []
        self.subdirs = {}

    def attach(self, path, srcfile):
        # print("attach", self.name, path)
        parts = psplit(path)
        if len(parts) == 1:
            # print(" => file")
            self.files.append(FileNode(srcfile, parent=self))
        else:
            # print(" => dir")
            node, other = parts
            if not node in self.subdirs:
                self.subdirs[node] = DirNode(node, parent=self)
            self.subdirs[node].attach(other, srcfile)

    @property
    def path(self):
        if self.parent is not None:
            return os.path.join(self.parent.path, self.name)
        else:
            return self.name

    def walk(self):
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



class FileNode(TreeNode):
    def __init__(self, srcfile, parent):
        super(FileNode, self).__init__(parent=parent)
        self.srcfile = srcfile
        self.is_file = True
        self.is_dir = False
        self.children = []

    @property
    def name(self):
        return self.srcfile.name

    def __repr__(self):
        return 'FileNode(srcfile=%s, path="%s")' % (self.srcfile, self.path)

    def count_items(self):
        return len(self.srcfile.items)


class DirNode(TreeNode):
    def __init__(self, name, parent=None):
        super(DirNode, self).__init__(parent=parent)
        self.name = name
        self.is_file = False
        self.is_dir = True

    @property
    def children(self):
        for _, v in self.subdirs.items():
            yield v
        for f in self.files:
            yield f

    def count_items(self):
        return sum([c.count_items() for c in self.children])

    def __repr__(self):
        return 'DirNode(name="%s", path="%s")' % (self.name, self.path)

class SourceFile:
    def __init__(self, raw_path, items=None, normpath=os.path.normpath):
        self.raw_path = raw_path
        self.path = normpath(raw_path)
        self.name = os.path.basename(self.path)
        self.items = items or []

    def add_item(self, item):
        self.items.append(item)
        item.set_srcfile(self)

    def add_items(self, items):
        for item in items:
            self.add_item(item)

    def __repr__(self):
        itstr = "\n\t%s\n" if len(self.items) > 0 else "%s"
        p = (self.name, self.raw_path, self.path, itstr % ",\n\t".join(map(repr, self.items)))
        return 'SourceFile(name="%s", raw_path="%s", path="%s", items=[%s])' % p

    @property
    def report_file_name(self):
        p = self.path
        if p.startswith("/"):
            p = p[1:]
        return p.replace("/", "_")+".html"

def make_file_tree(files):
    root_name, _ = psplit(files[0].path)
    root = DirNode(root_name)

    for f in files:
        # print(f.path, f.raw_path)
        parts = psplit(f.path)
        if len(parts) == 1:
            root.attach(parts[0], f)
        else:
            node, other = parts
            root.attach(other, f)
    return root
