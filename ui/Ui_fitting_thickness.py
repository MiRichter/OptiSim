# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'L:\05_Python\OptiSim V0.4.0\ui\fitting_thickness.ui'
#
# Created: Fri Nov 20 10:38:57 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(290, 107)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.layersCB = QtWidgets.QComboBox(Dialog)
        self.layersCB.setObjectName("layersCB")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.layersCB)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.referencesCB = QtWidgets.QComboBox(Dialog)
        self.referencesCB.setObjectName("referencesCB")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.referencesCB)
        self.noOfIterationsSB = QtWidgets.QSpinBox(Dialog)
        self.noOfIterationsSB.setMinimum(1)
        self.noOfIterationsSB.setMaximum(9999)
        self.noOfIterationsSB.setProperty("value", 100)
        self.noOfIterationsSB.setObjectName("noOfIterationsSB")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.noOfIterationsSB)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Layer thickness fitting menu"))
        self.label.setText(_translate("Dialog", "Layer:"))
        self.label_2.setText(_translate("Dialog", "Fit to:"))
        self.label_3.setText(_translate("Dialog", "max. Number of iterations:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

