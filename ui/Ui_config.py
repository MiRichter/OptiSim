# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Work\04_Python\OptiSim V0.5.0_alpha\ui\config.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(607, 474)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.loadLastFileCB = QtWidgets.QCheckBox(Dialog)
        self.loadLastFileCB.setObjectName("loadLastFileCB")
        self.verticalLayout_4.addWidget(self.loadLastFileCB)
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_9 = QtWidgets.QLabel(self.groupBox_5)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_8.addWidget(self.label_9)
        self.spectrumCB = QtWidgets.QComboBox(self.groupBox_5)
        self.spectrumCB.setObjectName("spectrumCB")
        self.horizontalLayout_8.addWidget(self.spectrumCB)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_16 = QtWidgets.QLabel(self.groupBox_5)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_3.addWidget(self.label_16)
        self.intensitySlider = QtWidgets.QSlider(self.groupBox_5)
        self.intensitySlider.setMinimumSize(QtCore.QSize(100, 0))
        self.intensitySlider.setMaximum(100)
        self.intensitySlider.setProperty("value", 100)
        self.intensitySlider.setOrientation(QtCore.Qt.Horizontal)
        self.intensitySlider.setObjectName("intensitySlider")
        self.horizontalLayout_3.addWidget(self.intensitySlider)
        self.intensityLabel = QtWidgets.QLabel(self.groupBox_5)
        self.intensityLabel.setObjectName("intensityLabel")
        self.horizontalLayout_3.addWidget(self.intensityLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_8 = QtWidgets.QLabel(self.groupBox_5)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_3.addWidget(self.label_8)
        self.angleSB = QtWidgets.QSpinBox(self.groupBox_5)
        self.angleSB.setMaximum(89)
        self.angleSB.setObjectName("angleSB")
        self.horizontalLayout_3.addWidget(self.angleSB)
        self.label_19 = QtWidgets.QLabel(self.groupBox_5)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_3.addWidget(self.label_19)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_14 = QtWidgets.QLabel(self.groupBox_5)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_7.addWidget(self.label_14)
        self.polTERB = QtWidgets.QRadioButton(self.groupBox_5)
        self.polTERB.setChecked(True)
        self.polTERB.setObjectName("polTERB")
        self.horizontalLayout_7.addWidget(self.polTERB)
        self.polTMRB = QtWidgets.QRadioButton(self.groupBox_5)
        self.polTMRB.setChecked(False)
        self.polTMRB.setObjectName("polTMRB")
        self.horizontalLayout_7.addWidget(self.polTMRB)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.dial_2 = QtWidgets.QDial(self.groupBox_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dial_2.sizePolicy().hasHeightForWidth())
        self.dial_2.setSizePolicy(sizePolicy)
        self.dial_2.setMinimum(-90)
        self.dial_2.setMaximum(90)
        self.dial_2.setSingleStep(90)
        self.dial_2.setPageStep(90)
        self.dial_2.setObjectName("dial_2")
        self.horizontalLayout_10.addWidget(self.dial_2)
        self.label_5 = QtWidgets.QLabel(self.groupBox_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_10.addWidget(self.label_5)
        self.polSB = QtWidgets.QSpinBox(self.groupBox_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.polSB.sizePolicy().hasHeightForWidth())
        self.polSB.setSizePolicy(sizePolicy)
        self.polSB.setMinimumSize(QtCore.QSize(100, 0))
        self.polSB.setMinimum(-90)
        self.polSB.setMaximum(90)
        self.polSB.setSingleStep(90)
        self.polSB.setObjectName("polSB")
        self.horizontalLayout_10.addWidget(self.polSB)
        self.verticalLayout_3.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_2.addWidget(self.groupBox_5)
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 3, 0, 1, 1)
        self.startSB = QtWidgets.QSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startSB.sizePolicy().hasHeightForWidth())
        self.startSB.setSizePolicy(sizePolicy)
        self.startSB.setMinimumSize(QtCore.QSize(80, 0))
        self.startSB.setMinimum(100)
        self.startSB.setMaximum(9999)
        self.startSB.setObjectName("startSB")
        self.gridLayout_2.addWidget(self.startSB, 0, 1, 1, 1)
        self.endSB = QtWidgets.QSpinBox(self.groupBox)
        self.endSB.setMinimumSize(QtCore.QSize(80, 0))
        self.endSB.setMinimum(100)
        self.endSB.setMaximum(9999)
        self.endSB.setObjectName("endSB")
        self.gridLayout_2.addWidget(self.endSB, 1, 1, 1, 1)
        self.stepSB = QtWidgets.QSpinBox(self.groupBox)
        self.stepSB.setMinimumSize(QtCore.QSize(80, 0))
        self.stepSB.setMinimum(1)
        self.stepSB.setMaximum(999)
        self.stepSB.setObjectName("stepSB")
        self.gridLayout_2.addWidget(self.stepSB, 2, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.horizontalLayout_2.addWidget(self.groupBox)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pathButton = QtWidgets.QPushButton(self.groupBox_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pathButton.sizePolicy().hasHeightForWidth())
        self.pathButton.setSizePolicy(sizePolicy)
        self.pathButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.pathButton.setObjectName("pathButton")
        self.horizontalLayout.addWidget(self.pathButton)
        self.pathEdit = QtWidgets.QLineEdit(self.groupBox_4)
        self.pathEdit.setObjectName("pathEdit")
        self.horizontalLayout.addWidget(self.pathEdit)
        self.reloadButton = QtWidgets.QPushButton(self.groupBox_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reloadButton.sizePolicy().hasHeightForWidth())
        self.reloadButton.setSizePolicy(sizePolicy)
        self.reloadButton.setMaximumSize(QtCore.QSize(60, 16777215))
        self.reloadButton.setObjectName("reloadButton")
        self.horizontalLayout.addWidget(self.reloadButton)
        self.verticalLayout_6.addWidget(self.groupBox_4)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_12 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.verticalLayout.addWidget(self.label_12)
        self.LBcorrectForReflCB = QtWidgets.QCheckBox(self.groupBox_2)
        self.LBcorrectForReflCB.setObjectName("LBcorrectForReflCB")
        self.verticalLayout.addWidget(self.LBcorrectForReflCB)
        self.line_2 = QtWidgets.QFrame(self.groupBox_2)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.label_11 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.verticalLayout.addWidget(self.label_11)
        self.gradingAdvancedCB = QtWidgets.QCheckBox(self.groupBox_2)
        self.gradingAdvancedCB.setObjectName("gradingAdvancedCB")
        self.verticalLayout.addWidget(self.gradingAdvancedCB)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_13 = QtWidgets.QLabel(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_9.addWidget(self.label_13)
        self.gradingMeshPointsSB = QtWidgets.QSpinBox(self.groupBox_2)
        self.gradingMeshPointsSB.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gradingMeshPointsSB.sizePolicy().hasHeightForWidth())
        self.gradingMeshPointsSB.setSizePolicy(sizePolicy)
        self.gradingMeshPointsSB.setMaximumSize(QtCore.QSize(60, 16777215))
        self.gradingMeshPointsSB.setMaximum(900)
        self.gradingMeshPointsSB.setProperty("value", 5)
        self.gradingMeshPointsSB.setObjectName("gradingMeshPointsSB")
        self.horizontalLayout_9.addWidget(self.gradingMeshPointsSB)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.line = QtWidgets.QFrame(self.groupBox_2)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.verticalLayout.addWidget(self.label_10)
        self.roughEMACB = QtWidgets.QCheckBox(self.groupBox_2)
        self.roughEMACB.setObjectName("roughEMACB")
        self.verticalLayout.addWidget(self.roughEMACB)
        self.frame = QtWidgets.QFrame(self.groupBox_2)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.EMA_mean = QtWidgets.QRadioButton(self.frame)
        self.EMA_mean.setObjectName("EMA_mean")
        self.horizontalLayout_4.addWidget(self.EMA_mean)
        self.EMA_Bruggemann = QtWidgets.QRadioButton(self.frame)
        self.EMA_Bruggemann.setObjectName("EMA_Bruggemann")
        self.horizontalLayout_4.addWidget(self.EMA_Bruggemann)
        self.EMA_MaxwellGarnett = QtWidgets.QRadioButton(self.frame)
        self.EMA_MaxwellGarnett.setObjectName("EMA_MaxwellGarnett")
        self.horizontalLayout_4.addWidget(self.EMA_MaxwellGarnett)
        self.verticalLayout.addWidget(self.frame)
        self.roughFresnelCB = QtWidgets.QCheckBox(self.groupBox_2)
        self.roughFresnelCB.setObjectName("roughFresnelCB")
        self.verticalLayout.addWidget(self.roughFresnelCB)
        self.calcDiffuseLightCB = QtWidgets.QCheckBox(self.groupBox_2)
        self.calcDiffuseLightCB.setChecked(True)
        self.calcDiffuseLightCB.setObjectName("calcDiffuseLightCB")
        self.verticalLayout.addWidget(self.calcDiffuseLightCB)
        self.frame_2 = QtWidgets.QFrame(self.groupBox_2)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_6 = QtWidgets.QLabel(self.frame_2)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.RaytracerIterationsSB = QtWidgets.QSpinBox(self.frame_2)
        self.RaytracerIterationsSB.setMinimum(1)
        self.RaytracerIterationsSB.setMaximum(9999)
        self.RaytracerIterationsSB.setProperty("value", 100)
        self.RaytracerIterationsSB.setObjectName("RaytracerIterationsSB")
        self.horizontalLayout_6.addWidget(self.RaytracerIterationsSB)
        self.label_7 = QtWidgets.QLabel(self.frame_2)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_6.addWidget(self.label_7)
        self.RaytracerIntensitySB = ScientificDoubleSpinBox(self.frame_2)
        self.RaytracerIntensitySB.setDecimals(9)
        self.RaytracerIntensitySB.setMaximum(1.0)
        self.RaytracerIntensitySB.setSingleStep(0.0001)
        self.RaytracerIntensitySB.setProperty("value", 0.001)
        self.RaytracerIntensitySB.setObjectName("RaytracerIntensitySB")
        self.horizontalLayout_6.addWidget(self.RaytracerIntensitySB)
        self.verticalLayout.addWidget(self.frame_2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout_5.addWidget(self.groupBox_2)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout_4.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_4.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(1)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.dial_2.valueChanged['int'].connect(self.polSB.setValue)
        self.polSB.valueChanged['int'].connect(self.dial_2.setValue)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Simulation property menu"))
        self.loadLastFileCB.setText(_translate("Dialog", "load last file when starting application"))
        self.groupBox_5.setTitle(_translate("Dialog", "Excitation"))
        self.label_9.setText(_translate("Dialog", "illumination spectrum:"))
        self.label_16.setText(_translate("Dialog", "intensity"))
        self.intensityLabel.setText(_translate("Dialog", "100%"))
        self.label_8.setText(_translate("Dialog", "angle"))
        self.label_19.setText(_translate("Dialog", "°"))
        self.label_14.setText(_translate("Dialog", "polarization:"))
        self.polTERB.setText(_translate("Dialog", "TE (s)"))
        self.polTMRB.setText(_translate("Dialog", "TM (p)"))
        self.label_5.setText(_translate("Dialog", "pol angle [°]:"))
        self.groupBox.setTitle(_translate("Dialog", "spectrum"))
        self.label_4.setText(_translate("Dialog", "wavelength (nm)"))
        self.label.setText(_translate("Dialog", "start value"))
        self.label_2.setText(_translate("Dialog", "end value"))
        self.label_3.setText(_translate("Dialog", "step"))
        self.groupBox_4.setTitle(_translate("Dialog", "path to material database"))
        self.pathButton.setText(_translate("Dialog", "..."))
        self.reloadButton.setText(_translate("Dialog", "reload"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "settings"))
        self.groupBox_2.setTitle(_translate("Dialog", "calculation options"))
        self.label_12.setText(_translate("Dialog", "Lambert-Beer"))
        self.LBcorrectForReflCB.setText(_translate("Dialog", "correct incomning ligth for reflection reference if available"))
        self.label_11.setText(_translate("Dialog", "grading"))
        self.gradingAdvancedCB.setText(_translate("Dialog", "use energy interpolation (y interpolation instead)"))
        self.label_13.setText(_translate("Dialog", "number of mesh points of one sublayer:"))
        self.label_10.setText(_translate("Dialog", "roughness model"))
        self.roughEMACB.setText(_translate("Dialog", "use EMA roughness layer:"))
        self.EMA_mean.setText(_translate("Dialog", "mean"))
        self.EMA_Bruggemann.setText(_translate("Dialog", "Bruggemann"))
        self.EMA_MaxwellGarnett.setText(_translate("Dialog", "Maxwell-Garnett"))
        self.roughFresnelCB.setText(_translate("Dialog", "use modified Fresnel coeffizients"))
        self.calcDiffuseLightCB.setText(_translate("Dialog", "include diffuse light (raytracer) if Haze > 0"))
        self.label_6.setText(_translate("Dialog", "max. no. of iterations"))
        self.label_7.setText(_translate("Dialog", "min. intensity"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "options"))

from ui.scientificspin import ScientificDoubleSpinBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

