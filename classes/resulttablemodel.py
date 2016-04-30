from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ResultTableModel(QAbstractTableModel):

    def __init__(self):
        #super(ResultTableModel, self).__init__() #seit Python 3 einfach:
        super().__init__()
        self.stacks = []
        self.dirty = False
        self.LabelList = []
        
    def sortByName(self):
        self.stacks = sorted(self.stacks)
        self.reset()

#   flags to set editable
#    def flags(self, index):
#        if not index.isValid():
#            return Qt.ItemIsEnabled
#        return Qt.ItemFlags(
#                QAbstractTableModel.flags(self, index)|
#                Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
            not (0 <= index.row() < len(self.stacks))):
            return None
        stack = self.stacks[index.row()]
        column = index.column()
        value = ''
        if role == Qt.DisplayRole:
            if column == 0:
                return stack.stackname
            for i, data in enumerate(self.LabelList):
                if column - 1 == i:
                    if 'layerwise' in data:
                        for i in stack.scalars[data]:
                            value = value + '%.4g' % i + '\\' 
                    else:
                        value = stack.scalars[data]
                    if isinstance(value, str):
                        return value
                    else:
                        return '%.4g' % value
#            elif column == ABSORPTION:
#                return stack.Anum ' 
#            elif column == REFLECTION:
#                return stack.Rnum
#            elif column == TRANSMISSION:
#                return stack.Tnum
        return None


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            return int(Qt.AlignRight|Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == 0:
                return 'stack name'
            for i, name in enumerate(self.LabelList):
                if section - 1 == i:
                    return name
        return int(section + 1)

    def rowCount(self, index=QModelIndex()):
        return len(self.stacks)

    def columnCount(self, index=QModelIndex()):
        return len(self.LabelList)+1

#    def setData(self, index, value, role=Qt.EditRole):
#        if index.isValid() and 0 <= index.row() < len(self.stacks):
#            stack = self.stacks[index.row()]
#            column = index.column()
#            if column == NAME:
#                stack.stackname = value
#            self.dirty = True
#            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
#                      index, index)
#            return True
#        return False

#    def insertRows(self, position, rows=1, index=QModelIndex()):
#        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
#        for row in range(rows):
#            self.stacks.insert(position + row,
#                              Ship(" Unknown", " Unknown", " Unknown"))
#        self.endInsertRows()
#        self.dirty = True
#        return True

#    def removeRows(self, position, rows=1, index=QModelIndex()):
#        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
#        self.ships = (self.ships[:position] +
#                      self.ships[position + rows:])
#        self.endRemoveRows()
#        self.dirty = True
#        return True

