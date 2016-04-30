# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'L:\05_Python\OptiSim V0.4.0\ui\defaults.ui'
#
# Created: Fri Nov 20 10:38:56 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tab2 = QtWidgets.QTabWidget(Dialog)
        self.tab2.setObjectName("tab2")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.scalarListView = QtWidgets.QListView(self.tab)
        self.scalarListView.setObjectName("scalarListView")
        self.horizontalLayout.addWidget(self.scalarListView)
        self.tab2.addTab(self.tab, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.calculationsListView = QtWidgets.QListView(self.tab_3)
        self.calculationsListView.setObjectName("calculationsListView")
        self.horizontalLayout_2.addWidget(self.calculationsListView)
        self.tab2.addTab(self.tab_3, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.plotListView = QtWidgets.QListView(self.tab_2)
        self.plotListView.setObjectName("plotListView")
        self.horizontalLayout_3.addWidget(self.plotListView)
        self.tab2.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tab2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tab2.setCurrentIndex(1)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Defaults menu"))
        self.tab2.setTabText(self.tab2.indexOf(self.tab), _translate("Dialog", "scalar values"))
        self.tab2.setTabText(self.tab2.indexOf(self.tab_3), _translate("Dialog", "calculations"))
        self.tab2.setTabText(self.tab2.indexOf(self.tab_2), _translate("Dialog", "plots"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

