# classes for the treeView and model in adavenced fitting Dialog

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex

class BranchNode(object):

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.parent = parent
        self.children = []

    def toString(self):
        return self.name

    def childAtRow(self, row):
        assert 0 <= row < len(self.children)
        return self.children[row]
        
    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1

    def insertChild(self, child):
        child.parent = self
        self.children.append(child)


class LeafNode(object):

    def __init__(self, fields, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.fields = fields

    def toString(self, separator="\t"):
        return separator.join(self.fields)

    def asRecord(self):
        record = []
        branch = self.parent
        while branch is not None:
            record.insert(0, branch.toString())
            branch = branch.parent
        assert record and not record[0]
        record = record[1:]
        return record + self.fields


class TreeOfParametersModel(QAbstractItemModel):


    def __init__(self, parent=None):
        super().__init__()
        self.columns = 0
        self.root = BranchNode("")
        self.headers = []

    def addBranch(self):
        pass
        
    def addRecord(self, fields, callReset=True):
        assert len(fields) > self.nesting
        root = self.root
        branch = None
        for i in range(self.nesting):
            key = fields[i].lower()
            branch = root.childWithKey(key)
            if branch is not None:
                root = branch
            else:
                branch = BranchNode(fields[i])
                root.insertChild(branch)
                root = branch
        assert branch is not None
        items = fields[self.nesting:]
        self.columns = max(self.columns, len(items))
        branch.insertChild(LeafNode(items, branch))
        if callReset:
            self.reset()


    def asRecord(self, index): # change this to get best output for applying fitting
        leaf = self.nodeFromIndex(index)
        if leaf is not None and isinstance(leaf, LeafNode):
            return leaf.asRecord()
        return []


    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None or isinstance(node, LeafNode):
            return 0
        return len(node)


    def columnCount(self, parent):
        return self.columns


    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop|Qt.AlignLeft)
        if role != Qt.DisplayRole:
            return None
        node = self.nodeFromIndex(index)
        assert node is not None
        if isinstance(node, BranchNode):
            return node.toString() if index.column() == 0 else ""
        return node.field(index.column())


    def headerData(self, section, orientation, role):
        if (orientation == Qt.Horizontal and
            role == Qt.DisplayRole):
            assert 0 <= section <= len(self.headers)
            return self.headers[section]
        return None


    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))


    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)


    def nodeFromIndex(self, index):
        return (index.internalPointer()
                if index.isValid() else self.root)



