# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'L:\05_Python\OptiSim V0.4.0\ui\resultdetails.ui'
#
# Created: Fri Nov 20 10:38:55 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ResultDetailDlg(object):
    def setupUi(self, ResultDetailDlg):
        ResultDetailDlg.setObjectName("ResultDetailDlg")
        ResultDetailDlg.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ResultDetailDlg)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtWidgets.QTableWidget(ResultDetailDlg)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.okButton = QtWidgets.QPushButton(ResultDetailDlg)
        self.okButton.setObjectName("okButton")
        self.verticalLayout.addWidget(self.okButton)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(ResultDetailDlg)
        self.okButton.clicked.connect(ResultDetailDlg.accept)
        QtCore.QMetaObject.connectSlotsByName(ResultDetailDlg)

    def retranslateUi(self, ResultDetailDlg):
        _translate = QtCore.QCoreApplication.translate
        ResultDetailDlg.setWindowTitle(_translate("ResultDetailDlg", "Result details"))
        self.okButton.setText(_translate("ResultDetailDlg", "Ok"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ResultDetailDlg = QtWidgets.QDialog()
    ui = Ui_ResultDetailDlg()
    ui.setupUi(ResultDetailDlg)
    ResultDetailDlg.show()
    sys.exit(app.exec_())

