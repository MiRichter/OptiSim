# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'L:\05_Python\OptiSim V0.4.0\ui\calculatedvalues.ui'
#
# Created: Fri Nov 20 10:38:55 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConfigTableViewWidget(object):
    def setupUi(self, ConfigTableViewWidget):
        ConfigTableViewWidget.setObjectName("ConfigTableViewWidget")
        ConfigTableViewWidget.resize(400, 300)
        ConfigTableViewWidget.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConfigTableViewWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ValueListView = QtWidgets.QListView(ConfigTableViewWidget)
        self.ValueListView.setObjectName("ValueListView")
        self.verticalLayout.addWidget(self.ValueListView)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConfigTableViewWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ConfigTableViewWidget)
        self.buttonBox.accepted.connect(ConfigTableViewWidget.accept)
        self.buttonBox.rejected.connect(ConfigTableViewWidget.reject)
        QtCore.QMetaObject.connectSlotsByName(ConfigTableViewWidget)

    def retranslateUi(self, ConfigTableViewWidget):
        _translate = QtCore.QCoreApplication.translate
        ConfigTableViewWidget.setWindowTitle(_translate("ConfigTableViewWidget", "Calculatd values"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ConfigTableViewWidget = QtWidgets.QDialog()
    ui = Ui_ConfigTableViewWidget()
    ui.setupUi(ConfigTableViewWidget)
    ConfigTableViewWidget.show()
    sys.exit(app.exec_())

