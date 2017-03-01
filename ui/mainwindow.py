# -*- coding: utf-8 -*-

import os
import sys
import traceback

import matplotlib
"""
Module implementing MainWindow.
"""
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import pyqtSlot
# from PyQt5.QtGui import 
from PyQt5.QtWidgets import QMainWindow


import time
import pickle
import glob # for deleting tmp files
import numpy as np
import numexpr as ne

import qrc_resource
import helpform
import logging

import scipy
from scipy.optimize import minimize # minimize_scalar, basinhopping, curve_fit
#import tmm.examples
#from math import *

from .Ui_mainwindow_tool import Ui_MainWindow
from .Ui_subwindow import Subwindow
from .Ui_esubwindow import ESubwindow
from .calculatedvalues import ConfigTableViewWidget
from .resultdetails import ResultDetailDlg
from .references import ReferencesDlg
from .config import ConfigDlg
from .gradingfiles import GradingFilesDlg
from .dielectric_function import dielectricFunctionDlg
from .batchmenu import BatchDlg
from .fitting_thickness import FittingThicknessDlg
from .fitting_diffusion import FittingDiffusion
from .fitting_advanced import FittingAdvancedDlg
from .extractbandgap import ExtractBandgapDlg
from .color import ColorDlg

import strings

from classes.errors import *
from classes.layer import Layer
from classes.layerstack import LayerStack
from classes.optics import Optics
from classes.resulttablemodel import ResultTableModel
from classes.navtoolbar import NavToolBar as NavigationToolbar

__version__ = "0.6.0"

 
def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            raise LoadError('Can not convert string {} into number!'.format(s))

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.setWindowTitle("OptiSim - Version: " + __version__)

        # additional widget properties
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setFixedWidth(200)
        self.statusbar.addPermanentWidget(self.progressBar)

        
        # define empty variables
        self.fileName = None
        self.dirty = False  # set False when saved, True when changes made
        self.layerSwitched = True
        
        #------------ Application Settings ------------------
        
        self.AppSettings = QtCore.QSettings('settings.ini', QtCore.QSettings.IniFormat)
        self.AppSettings.setFallbacksEnabled(False)    # File only, no fallback to registry or or.

        self.recentFiles = self.AppSettings.value("RecentFiles") or []
        self.lastFile = self.AppSettings.value("LastFile")
        #self.restoreGeometry(settings.value("MainWindow/Geometry", QtCore.QByteArray()))
        #self.restoreState(settings.value("MainWindow/State", QtCore.QByteArray()))
        
        self.createActions()
        self.createMenus()
        self.createToolBars()
        #self.createStatusBar()
        #self.updateMenus()
        
        self.windowMapper = QtCore.QSignalMapper(self)
        self.windowMapper.mapped[QtWidgets.QWidget].connect(self.setActiveSubWindow)
        
        self.PlotToolBar = QtWidgets.QToolBar()

        self.PlotToolBar.setFloatable(True)
        self.PlotToolBar.setMovable(True)
        self.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea), self.PlotToolBar)

        self.criSourcePossibilities = ['from database', 'from file', 'constant', 'graded', 'dielectric function']
        self.criSourceSelection.addItems(self.criSourcePossibilities)
        
        self.collectionPossibilities = ['from collection function', 'from diffusion length']
        self.collectionSelection.addItems(self.collectionPossibilities)
        
        self.resultlist = []
        self.resultNames = {}
        
        #------------ Defaults and settings -------------------
        
        # which scalar results shall be shown by default
        self.calcOptionsCB = [self.calcStackOpticsCB, self.calcFieldIntensityCB, self.calcLayerwiseOpticsCB, 
                            self.calcQECB, self.calcGenerationCB, self.calcEllipsometryCB, self.calcOptBeamCB]
        self.plotOptionsCB = [self.plotStackOpticsCB, self.plotFieldIntensityCB, self.plotLayerwiseOpticsCB, 
                            self.plotQECB, self.plotGenerationCB, self.plotEllipsometryCB, self.plotOptBeamCB]
        calculations = [0] # indices of calcOptions
        plots = [0] # indices of plotOPtions
        
        scalars = ['reflectance (%)', 'transmittance (%)', 'absorbance (%)']
        self.defaults = dict([
                        ('scalars', scalars), 
                        ('plots', plots), 
                        ('calculations', calculations)
                        ])
        
        wavelengthRange = [350, 1300, 5]

        MaterialDBPath = os.getcwd() + "\\materialDB"
        Spectrum = "AM1.5G_ed2.9.dat"
        #self.currentworkingdirectory = 
        #load Material database
        self.settings = dict([
                        ('MaterialDBPath', MaterialDBPath),
                        ('wavelengthRange', wavelengthRange),
                        ('wavelength', np.arange(wavelengthRange[0], wavelengthRange[1] + wavelengthRange[2], wavelengthRange[2])),  
                        ('angle', 0), 
                        ('polarization', 0),  # 0 => TE(s) 1 => TM (p)
                        ('LB correct for Reflection', True),
                        ('grading advanced', True),
                        ('roughness EMA model', True),
                        ('roughness Fresnel model', False),
                        ('roughness Haze calc diffuse', [True, 100, 0.00001]), # calc diffuse light, max iterations, min intensity 
                        ('EMA model',  1), # 0 => mean, 1 => Bruggemann, 2 => Maxwell-Garnett
                        ('intensity', 100),  # % prefactor for incident light intensity
                        ('spectrum', Spectrum)
                        ])
        
        self.references = dict([    
                        ('R reference', [os.getcwd() + '\\references\\R.dat', 1]), 
                        ('T reference', ['', 0]), 
                        ('EQE reference', [os.getcwd() + '\\references\\EQE.dat', 1]), 
                        ('psi reference', ['', 0]), 
                        ('delta reference', ['', 0])
                        ])
        
        self.batchVariables = []
            
        #create raw buttongoup for layer buttons
        self.ButtonGroup = QtWidgets.QButtonGroup(self.StackFrame)
        
        MainWindowStyleSheet = strings.styleSheetMainWindow()
        StackFrameStyleSheet = strings.styleSheetFrame()
        self.setStyleSheet(MainWindowStyleSheet)
        self.StackFrame.setStyleSheet(StackFrameStyleSheet)
       # self.colorButton.setStyleSheet('background: black; border-color: black;border-width: 1px;')
        
      
        # change overlap of dockwidget
        self.setCorner(QtCore.Qt.BottomLeftCorner, QtCore.Qt.LeftDockWidgetArea)
        self.recVelLE.setMaximum(1e12)
        
        # create model/view architecture for results
        self.resultmodel = ResultTableModel()
        self.ResultTableView.setModel(self.resultmodel)
        

        
        #------- CONNECTIONS ------------------------------
        
        # define SIGNAL-SLOT connections
        self.ButtonGroup.buttonClicked[int].connect(self.SelectedLayerClicked)
        #self.sroughGroup.toggled.connect(self.sroughChanged)
        #self.hazeSlider.valueChanged.connect(self.hazeValueChanged)
        #self.criSourceSelection.currentIndexChanged[str].connect(self.criSourceSelected)
        #self.criDBList.currentItemChanged.connect(self.criDBChanged)
        #self.criFilePathButton.clicked.connect(self.criFilePathSelected)
            #TODO: editable Filepath
        #self.criFileGroupBox.toggled.connect(self.criFileAlphaChanged)
        #self.criFileSpinBox.valueChanged.connect(self.criFileAlphaChanged)
        #self.criConstantnEdit.valueChanged.connect(self.criConstantChanged)
        #self.criConstantkEdit.valueChanged.connect(self.criConstantChanged)
        
        #self.collectionSelection.currentIndexChanged[str].connect(self.collectionSelected)
        #self.colFunctionInput.editingFinished.connect(self.collectionChanged)
        self.colFunctionInput.textChanged.connect(self.checkFunctionInput)
        self.gradingFunctionInput.textChanged.connect(self.checkFunctionInput)
        # emit the signal one time for init
        self.colFunctionInput.textChanged.emit(self.colFunctionInput.text())
        
        self.ResultTableView.selectionModel().selectionChanged.connect(self.fillCurveList)
        self.ResultTableView.doubleClicked.connect(self.showResultDetails)
        #self.mdiArea.subWindowActivated.connect(self.updateToolbar) 

        self.showMaximized()

        #------ START ROUTINE -----------------------------
        self.loadInitialFile()
        self.createStackView(0)
        #self.tabWidget.setCurrentIndex(0)
        self.dirty = False

    def createActions(self):
        '''
        createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):'''
                     
        # ----------- File
        self.stackOpenAction = self.createAction("&Open...", self.openStack,
                QtGui.QKeySequence.Open, "fileopen",
                "Open an existing image file")
        self.stackSaveAction = self.createAction("&Save", self.saveStack,
                QtGui.QKeySequence.Save, "filesave", "Save the stack")
        self.stackSaveAsAction = self.createAction("Save &As...",
                self.saveAsStack, icon="filesaveas",
                tip="Save the stack using a new name")
        self.quitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "quit", "Close the application")
        
        # ----------- Stack
        self.addAboveAction = self.createAction("Add &above", self.addAbove,
                None, "addAbove", 
                "add a new layer above the selected")
        self.addBelowAction = self.createAction("Add &below", self.addBelow,
                None, "addBelow", 
                "add a new layer below the selected")
        self.moveUpAction = self.createAction("Move &up", self.moveUp,
                None, "moveUp", 
                "move selected layer one position up")
        self.moveDownAction = self.createAction("Move &down", self.moveDown,
                None, "moveDown", 
                "move selected layer one position down")
        self.removeLayerAction = self.createAction("&Remove layer", self.removeLayer,
                None, "removeLayer",
                "remove selected layer")
        
        self.showReferencesAction = self.createAction("references ...", self.showReferences, 
                None, None, "define path for reference files")
        
        self.showAllCRIAction = self.createAction("Show all n,k values", self.showAllCRI, 
                None, None, "plots all complex refractive index spectra at once")
                
        
        # ----------- Simulation Menu
        self.runAction = self.createAction("&Run", self.runStack, 
                "Ctrl+H", "runStack", 
                "calculates current stack")
        self.defineBatchAction = self.createAction("&define batch ...", self.defineBatch, 
                None, None,
                "opens menu to define batch variables")
        self.runBatchAction = self.createAction("Run &batch", self.runBatch, 
                "Ctrl+B", "runBatch",
                "calculates batch variation")        
        
        # ----------- Fitting Menu
        self.fitThicknessAction = self.createAction("fit &thickness ...", self.fitThickness, 
                None, 'fit_t', 
                "opens menu to perform layer thickness fitting")
        self.fitDiffLengthAction = self.createAction("fit &diffusion length ...", self.fitDiffLength, 
                None, 'fit_D', 
                "opens menu to perform diffusion length fitting")
        self.fitAdvancedAction = self.createAction("&advanced fitting ...", self.fitAdvanced, 
                None, None, "opens menu to perform advenced fitting")
        
        # ----------- Config Menu
        self.configOpenAction = self.createAction("&Simulation properties", self.showConfig,
                None, 'settings', tip= "Open the configuration menu")
        
        # ----------- Results Menu
        self.saveDataAction = self.createAction("save data to text file...", self.saveData, 
                tip = "saves the numerical data shown in the active graph")
        self.showColorAction = self.createAction("show color...", self.showColor, 
                tip = "show the color of stacks from calculated reflection")
        self.showLogFileAction = self.createAction("show log file...", self.showLogFile, 
                tip = "show the log file of the latest simulation")
        self.saveSCAPSGenerationAction = self.createAction("export Generation for SCAPS...", self.saveSCAPSGeneration, 
                tip = "export the generation profile of the selected result (if available) in SCAPS format")
        self.saveSCAPSGenerationAction.setEnabled(False)
            
        
        # ----------- Window Menu
        self.windowCascadeAction = self.createAction("&Cascade",
                self.mdiArea.cascadeSubWindows, 
                "Ctrl+Alt+C", "cascadeAll",
                "arrange all windows by cascade")
        self.windowTileAction = self.createAction("&Tile",
                self.mdiArea.tileSubWindows, 
                "Ctrl+Alt+T", "tileAll",
                "arrange all windows abreastly")
        self.windowRestoreAction = self.createAction("&Restore All",
                self.windowRestoreAll, 
                "Ctrl+Alt+R", "restoreAll",
                "restore all windows to privios state")
        self.windowMinimizeAction = self.createAction("&Minimize All",
                self.windowMinimizeAll, 
                "Ctrl+Alt+M", "minimizeAll",
                "minimize all open windows")
        self.windowCloseAction = self.createAction("Cl&ose All",
                self.mdiArea.closeAllSubWindows, 
                "Ctrl+Alt+X", "closeAll",
                "close all windows")
        
        # ---------- Help Menu
        self.helpAboutAction = self.createAction("&About OptiSim",
                self.helpAbout)
        self.helpHelpAction = self.createAction("&Help", self.helpHelp,
                QtGui.QKeySequence.HelpContents)
        
    def createMenus(self):
        
        self.fileMenu = self.menuBar.addMenu("&File")
        self.fileMenuActions = (self.stackOpenAction,
                self.stackSaveAction, self.stackSaveAsAction, None, self.quitAction)
        self.fileMenu.aboutToShow.connect(self.updateFileMenu)
        self.updateFileMenu()
        
        self.stackMenu = self.menuBar.addMenu("&Stack")
        self.addActions(self.stackMenu, (self.addAboveAction, self.addBelowAction,
                            self.moveUpAction, self.moveDownAction, self.removeLayerAction, None, self.showReferencesAction, self.showAllCRIAction))
        
        simulationMenu = self.menuBar.addMenu("S&imulation")
        self.addActions(simulationMenu, (self.runAction, self.defineBatchAction, self.runBatchAction, None))
        
        fittingMenu = self.menuBar.addMenu("&Fitting")
        self.addActions(fittingMenu, (self.fitThicknessAction, self.fitDiffLengthAction, self.fitAdvancedAction, None))
        
        configMenu = self.menuBar.addMenu("S&ettings")
        self.addActions(configMenu, (self.configOpenAction, None))
        
        
        resultsMenu = self.menuBar.addMenu("&Results")
        self.addActions(resultsMenu, (self.showColorAction, self.showLogFileAction, None, self.saveDataAction, self.saveSCAPSGenerationAction, None))
        
        self.windowMenu = self.menuBar.addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar.addSeparator()
        
        helpMenu = self.menuBar.addMenu("&Help")
        self.addActions(helpMenu, (self.helpAboutAction, self.helpHelpAction))

#        self.helpMenu = self.menuBar().addMenu("&Help")
#        self.helpMenu.addAction(self.aboutAct)
#        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, (self.stackOpenAction,
                                      self.stackSaveAction))
        stackToolbar = self.addToolBar("Stack")
        stackToolbar.setObjectName("StackToolBar")
        self.addActions(stackToolbar, (self.addAboveAction, self.addBelowAction,
                    self.moveUpAction, self.moveDownAction, self.removeLayerAction))

        simulationToolBar = self.addToolBar("Simulation")
        simulationToolBar.setObjectName("SimulationToolbar")
        self.addActions(simulationToolBar, (self.runAction, self.runBatchAction, self.configOpenAction))
        
        windowToolBar = self.addToolBar("Window")
        windowToolBar.setObjectName("WindowToolbar")
        self.addActions(windowToolBar, (self.windowCascadeAction, self.windowTileAction, self.windowMinimizeAction,
                        self.windowRestoreAction, self.windowCloseAction))
        
        fitToolBar = self.addToolBar("Fitting")
        fitToolBar.setObjectName("FittingToolbar")
        self.addActions(fitToolBar, (self.fitThicknessAction, self.fitDiffLengthAction))
                        
                        
    def createStackView(self, selected):
        # draw stack button group from self.stack variable
        self.selectedLayer = selected
        self.currentLayer = self.stack[selected]
        for Button in self.ButtonGroup.buttons():
            self.ButtonGroup.removeButton(Button)
            #self.verticalStackLayout.removeWidget(Button)
            Button.deleteLater()
        for Position, layer in enumerate(self.stack):
            LayerButton = QtWidgets.QPushButton()
            LayerButton.setText('%s (%i nm)' %(layer.name, layer.thickness))
            LayerButton.setAutoExclusive(True)
            LayerButton.setCheckable(True)
            LayerButton.setStyleSheet('background-color: %s' %self.stack[Position].color.name())
            if Position == selected:
                LayerButton.setChecked(True)
                self.ShowLayerDetails()
            self.ButtonGroup.addButton(LayerButton, Position)
            self.verticalStackLayout.addWidget(LayerButton)
            #self.verticalStackLayout.show()
            
            
    def addBelow(self):
        """
        create new default layer as Layer class 
        """
        newlayername = self.getnewlayername()
        newLayer = Layer(newlayername, 100)
        pos = self.selectedLayer + 1
        self.stack.insert(pos, newLayer)
        self.createStackView(pos)
        self.dirty = True
        self.updateStatus("added new layer {} at bottom of stack".format(newlayername))
        

    def addAbove(self):
        """
        create new default layer as Layer class 
        """
        newlayername = self.getnewlayername()
        newLayer = Layer(newlayername, 100)
        pos = self.selectedLayer
        if pos < 0:
            pos = 0
            
        self.stack.insert(pos, newLayer)
        self.createStackView(pos)
        self.dirty = True
        self.updateStatus("added new layer {} on top of stack".format(newlayername))
        

    def removeLayer(self):
        """
        Slot documentation goes here.
        """
        if len(self.stack) == 1:
            return
        self.stack.pop(self.selectedLayer)
        if self.selectedLayer > 0:
            self.selectedLayer = self.selectedLayer -1
        else:
            self.selectedLayer = 0
        self.createStackView(self.selectedLayer)
        self.dirty = True
        self.updateStatus("removed layer {}".format(self.currentLayer.name))
    
    
    def resizeSlot(self):
        self.dockStackSetup.resize(0, 0)

    def moveUp(self):
        """
        moves the selected layer one position upwards until zero position
        """
        if self.selectedLayer > 0:
            self.stack[self.selectedLayer-1], self.stack[self.selectedLayer] = \
            self.stack[self.selectedLayer], self.stack[self.selectedLayer-1]
            self.selectedLayer = self.selectedLayer-1
            self.createStackView(self.selectedLayer)
            self.dirty = True
            self.updateStatus("changed stack order")
   
    def moveDown(self):
        """
        moves the selected layer one position downwards until bottommost position
        """
        if self.selectedLayer < len(self.stack)-1:
            self.stack[self.selectedLayer], self.stack[self.selectedLayer+1] = \
            self.stack[self.selectedLayer+1], self.stack[self.selectedLayer]
            self.selectedLayer = self.selectedLayer+1
        self.createStackView(self.selectedLayer)
        self.dirty = True
        self.updateStatus("changed stack order")


    def getnewlayername(self):
        '''
        find latest 'new layer' number and iterate for the new layer
        '''
        # method of counting all 'new layers', problem: when removing one 'new layer' creates duplicates
        layernames = ""
        for names in self.stack:
            layernames = layernames + " " + names.name
        newlayernumber = layernames.count('new layer')
        if newlayernumber == 0:
            newlayername = 'new layer 1'
        else:
            newlayername = 'new layer ' + str(newlayernumber+1)
        # method of finding numbers  of 'new layer' and add new one; problem: works only for bottom
#        newlayernumbers = []
#        if 'new layer' in layernames:
#                lastnumber = names.name.split()
#                newlayernumbers.append(int(lastnumber.pop()))
#                newlayernumbers.sort()
#                print(newlayernumbers)
#                addedlayernumber = newlayernumbers.pop()+1
#                newlayername = 'new layer ' + str(addedlayernumber)
#        else:
#            newlayername = 'new layer 1'
        return newlayername
    
    def SelectedLayerClicked(self,  index):
        self.selectedLayer = index
        self.currentLayer = self.stack[index]
        self.ShowLayerDetails()

    def ShowLayerDetails(self):
        # put layer properties to respective view widgets
        self.layerNameField.setText(self.currentLayer.name)
        self.colorButton.setStyleSheet('''QPushButton {
        border-style: outset;
        border-width: 1px;
        border-radius: 5px;
        font: bold 12px;
        color: black;
        background: %s;
        border-color: rgb(0, 103, 176);}''' %self.currentLayer.color.name())
        self.layerThicknessSB.setValue(self.currentLayer.thickness)
        self.thickLayerCB.setChecked(self.currentLayer.thick)
        self.fillSrough()
        
        criItem = self.criSourceSelection.findText(self.currentLayer.criSource)
        self.criSourceSelection.setCurrentIndex(criItem)
        self.fillCriSourceWidget()
        
        colItem = self.collectionSelection.findText(self.currentLayer.collection['source'])
        self.collectionSelection.setCurrentIndex(colItem)
        self.fillCollectionWidget()

        if self.currentLayer.mesh['meshing'] == 0:
            self.constantPointsRB.setChecked(True)
        elif self.currentLayer.mesh['meshing'] == 1:
            self.constantDistRB.setChecked(True)
        else:
            self.autoDistRB.setChecked(True)
        self.constantPointsSB.setValue(self.currentLayer.mesh['Points'])
        self.constantDistSB.setValue(self.currentLayer.mesh['Dist'])
        self.updateMeshPoints()

    def fillSimulationOptions(self):
        for i in self.defaults['calculations']:
            CB = self.calcOptionsCB[i]
            CB.setChecked(True)
        for i in self.defaults['plots']:
            CB = self.plotOptionsCB[i]
            CB.setChecked(True)
            
    def fillSrough(self):
        self.sroughGroup.setChecked(self.currentLayer.srough)
        self.sroughThicknessEdit.setValue(self.currentLayer.sroughThickness)
        
        self.hazeRSlider.setValue(self.currentLayer.sroughHazeR*100)
        self.hazeRLabel.setText(str(self.currentLayer.sroughHazeR))
        self.hazeTSlider.setValue(self.currentLayer.sroughHazeT*100)
        self.hazeTLabel.setText(str(self.currentLayer.sroughHazeT))
    
    def fillCriSourceWidget(self):
        layer = self.currentLayer
        # from database 
        DBItem = self.criDBList.findItems(layer.criDBName, QtCore.Qt.MatchFixedString)
        if DBItem:
            self.criDBList.setCurrentItem(DBItem[0])
        else:
            self.criDBList.setCurrentItem(self.criDBList.item(0))
        
        # from file
        self.criFileEdit.setText(layer.criFile['path'])
        self.criFileGroupBox.setChecked(layer.criFile['alpha'])
        self.criFileSpinBox.setValue(layer.criFile['n'])
        
        # constant
        self.criConstantnEdit.setValue(layer.criConstant[0])
        self.criConstantkEdit.setValue(layer.criConstant[1])
        
        # grading
        mode = self.currentLayer.criGrading['mode']
        value = self.currentLayer.criGrading['value']
        if mode == 'constant':
            self.gradingFunctionInput.setText(str(value))
        if mode == 'linear':
            self.gradingFunctionInput.setText('lin(%.3f,%.3f)' %(value[0], value[1]))
        if mode == 'function':
            self.gradingFunctionInput.setText(value)
        self.plotGradingFunction()  
        
        self.plotDielectricFunction()
        
    def fillCollectionWidget(self):
        mode = self.currentLayer.collection['mode']
        value = self.currentLayer.collection['value']
        SCRwidth = self.currentLayer.collection['SCRwidth']
        diffLength = self.currentLayer.collection['diffLength']
        recVel = self.currentLayer.collection['recVel']
        if 'grading' in self.currentLayer.collection:
            grading = self.currentLayer.collection['grading']
        else:
            grading = 0.0
            self.currentLayer.collection['grading'] = grading
            
        SCRside = self.currentLayer.collection['SCRside']
        
        # from collection function
        if mode == 'constant':
            self.colFunctionInput.setText(str(value))
        if mode == 'linear':
            self.colFunctionInput.setText('lin(%.3f,%.3f)' %(value[0], value[1]))
        if mode == 'function':
            self.colFunctionInput.setText(value)
        
        # from diffusion length
        self.SCRwidthSB.setValue(SCRwidth)
        self.diffLengthSB.setValue(diffLength)
        self.recVelLE.setValue(recVel)
        self.collectionGradingSB.setValue(grading)
        self.SCRtop.setChecked(SCRside)
        
        self.plotCollectionFunction()
   
    @pyqtSlot()
    def on_layerNameField_editingFinished(self):
        """
        when Layer name is edited, the layer property in layer class is changed
        """
        newName = self.layerNameField.text()
        self.currentLayer.name = newName
        self.ButtonGroup.checkedButton().setText('%s (%i nm)' %(newName, self.currentLayer.thickness))
        self.dirty = True
        self.updateStatus("changed name of selected layer to {}".format(newName))
   
    @pyqtSlot(int)
    def on_layerThicknessSB_valueChanged(self, p0):
        """
        when Layer thickness is edited, the layer property in layer class is changed
        """
        if not self.currentLayer.thickness == p0:
            self.currentLayer.thickness = p0
            self.ButtonGroup.checkedButton().setText('%s (%i nm)' %(self.currentLayer.name, self.currentLayer.thickness))
            self.currentLayer.makeXnodes()
            self.currentLayer.makeXcollection()
            self.currentLayer.makeXgrading()
            self.updateMeshPoints()
            self.dirty = True
            self.updateStatus("changed {} thickness to {}".format(
                                           self.currentLayer.name, p0))
      
    @pyqtSlot(bool)
    def on_thickLayerCB_toggled(self, checked):            
        self.currentLayer.thick = checked
        self.dirty = True
        self.updateStatus("changed {} to incoherent".format(self.currentLayer.name))
   
    @pyqtSlot(str)
    def on_collectionSelection_activated(self, p0):
        if not self.currentLayer.collection['source'] == p0:
            self.currentLayer.collection['source'] = p0
            self.currentLayer.makeXcollection()
            self.fillCollectionWidget()
            self.dirty = True
            self.updateStatus("changed source for collection for {} to {}".format(
                                           self.currentLayer.name, p0))
    
    def checkFunctionInput(self, p0): 
        #TODO: check input for constant, linear , function
        
        sender = self.sender()
        constantVal = QtGui.QDoubleValidator()
        #\\b(lin|LIN|Lin)\\b
        #decimal: ^(?:0|[1-9][0-9]*)\.[0-9]+$
        self.linearExp = QtCore.QRegExp("lin[\\(]([+-]?\\d*\\.?\\d+),\s*([+-]?\\d*\\.?\\d+)[\\)]")
        linearVal = QtGui.QRegExpValidator(self.linearExp)
        
        constState = constantVal.validate(sender.text(), 0)[0]
        linState = linearVal.validate(sender.text(), 0)[0]

        if constState == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
            self.functionOk = 'constant'
        elif linState == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
            self.functionOk = 'linear'
        elif constState == QtGui.QValidator.Intermediate or \
           linState == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
            self.functionOk = None
        elif self.checkFunction(p0):
            color = '#c4df9b' # green
            self.functionOk = 'function'
        else:
            color = '#f6989d' # red
            self.functionOk = None
        
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
 
    def checkFunction(self, func):
        try:
            x = self.currentLayer.x
            dx = self.currentLayer.thickness
            self.Func = ne.evaluate(func)
            return True
        except:
            return False

    @pyqtSlot()
    def on_gradingFunctionInput_editingFinished(self):
        if self.functionOk is not None:
            func = self.gradingFunctionInput.text()
            self.currentLayer.criGrading['mode'] = self.functionOk
            if self.functionOk == 'constant':
                func = func.replace(',', '.')
                self.gradingFunctionInput.setText(func)
                self.currentLayer.criGrading['value'] = float(func)
            elif self.functionOk == 'linear':
                self.linearExp.indexIn(func)
                a = float(self.linearExp.cap(1))
                b = float(self.linearExp.cap(2))
                self.currentLayer.criGrading['value'] = [a, b]
            elif self.functionOk == 'function':
                self.currentLayer.criGrading['value'] = func
                
            self.currentLayer.makeXgrading()
            self.plotGradingFunction()
            
    @pyqtSlot()
    def on_colFunctionInput_editingFinished(self):
        if self.functionOk is not None:
            func = self.colFunctionInput.text()
            self.currentLayer.collection['mode'] = self.functionOk
            if self.functionOk == 'constant':
                func = func.replace(',', '.')
                self.colFunctionInput.setText(func)
                self.currentLayer.collection['value'] = float(func)
            elif self.functionOk == 'linear':
                self.linearExp.indexIn(func)
                a = float(self.linearExp.cap(1))
                b = float(self.linearExp.cap(2))
                self.currentLayer.collection['value'] = [a, b]
            elif self.functionOk == 'function':
                self.currentLayer.collection['value'] = func
                
            self.currentLayer.makeXcollection()
            self.plotCollectionFunction()

    
    def plotGradingFunction(self):
        x = self.currentLayer.x
        xMole = self.currentLayer.xMole
        self.gradingPlot.canvas.ax.clear() 
        self.gradingPlot.canvas.ax.plot(x, xMole)
        self.gradingPlot.canvas.ax.set_xlabel('x $(nm)$')
        self.gradingPlot.canvas.ax.set_ylabel('xMole')
        self.gradingPlot.canvas.draw()
    
    def plotCollectionFunction(self):
        x = self.currentLayer.x
        fc = self.currentLayer.fc
        self.collectionPlot.canvas.ax.clear() 
        self.collectionPlot.canvas.ax.plot(x, fc)
        self.collectionPlot.canvas.ax.set_xlabel('x (nm)')
        self.collectionPlot.canvas.ax.set_ylabel('f_c')
        self.collectionPlot.canvas.draw()
    
    @pyqtSlot()
    def on_gradingFilesButton_clicked(self):
        dialog = GradingFilesDlg(self.currentLayer.criGrading['files'], self)
        if dialog.exec_():
            self.currentLayer.criGrading['files'] = dialog.files
    
    @pyqtSlot(bool)
    def on_sroughGroup_toggled(self, p0):
        if not self.currentLayer.srough == p0:
            self.currentLayer.srough = p0
            self.dirty = True
            self.updateStatus("changed roughness for {}".format(
                                       self.currentLayer.name))
    
    @pyqtSlot(int)
    def on_hazeRSlider_valueChanged(self, value):
        scaledValue = float(value)/100     #type of "value" is int so you need to convert it to float in order to get float type for "scaledValue" 
        self.hazeRLabel.setText(str(scaledValue))
        if not self.currentLayer.sroughHazeR == scaledValue:
            self.currentLayer.sroughHazeR = scaledValue
            self.dirty = True
            self.updateStatus("changed refelction haze for {} to {}".format(
                                           self.currentLayer.name, str(scaledValue)))
    
    @pyqtSlot(int)
    def on_hazeTSlider_valueChanged(self, value):
        scaledValue = float(value)/100     #type of "value" is int so you need to convert it to float in order to get float type for "scaledValue" 
        self.hazeTLabel.setText(str(scaledValue))
        if not self.currentLayer.sroughHazeT == scaledValue:
            self.currentLayer.sroughHazeT = scaledValue
            self.dirty = True
            self.updateStatus("changed transmission haze for {} to {}".format(
                                           self.currentLayer.name, str(scaledValue)))
                                           
    @pyqtSlot(str)
    def on_criSourceSelection_activated(self, p0):
        if not self.currentLayer.criSource == p0:
            self.currentLayer.criSource = p0
            self.dirty = True
            self.updateStatus("changed source for complex refractive index for {} to {}".format(
                                       self.currentLayer.name, p0))

    @pyqtSlot(float)
    def on_criConstantkEdit_valueChanged(self, p0):
        if not self.currentLayer.criConstant[1] == p0:
            n = self.currentLayer.criConstant[0]
            self.currentLayer.criConstant = [n, p0]
            self.dirty = True
            self.updateStatus("changed constant k for {} to {}".format(
                                       self.currentLayer.name, p0))
    
    @pyqtSlot(float)
    def on_criConstantnEdit_valueChanged(self, p0):
        if not self.currentLayer.criConstant[0] == p0:
            k = self.currentLayer.criConstant[1]
            self.currentLayer.criConstant = [float(p0), k]
            self.dirty = True
            self.updateStatus("changed constant n for {} to {}".format(
                                       self.currentLayer.name, p0))
    
    @pyqtSlot()
    def on_criFilePathButton_clicked(self):
        #TODO: make LineEdit editable for costum path input
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'select a file containing the nk or alpha data', os.getcwd()+'\\materialDB')
        if fileName:
            if not self.currentLayer.criFile['path'] == fileName:
                self.criFileEdit.setText(fileName)
                self.currentLayer.criFile['path'] = fileName
                self.dirty = True
                self.updateStatus("changed cri source file for {}".format(
                                       self.currentLayer.name))
    
    @pyqtSlot(bool)
    def on_criFileGroupBox_toggled(self, p0):
        if not self.currentLayer.criFile['alpha'] == p0:
            self.currentLayer.criFile['alpha'] = p0
            self.dirty = True
            self.updateStatus("changed cri source file with alpha for {}".format(
                                       self.currentLayer.name))
       
    @pyqtSlot(float)
    def on_criFileSpinBox_valueChanged(self, p0):
        if not self.currentLayer.criFile['n'] == p0:
            self.currentLayer.criFile['n'] = p0
            self.dirty = True
            self.updateStatus("changed cri source file with alpha for {}".format(
                                       self.currentLayer.name))
      
    @pyqtSlot(QtWidgets.QListWidgetItem, QtWidgets.QListWidgetItem)
    def on_criDBList_currentItemChanged(self, item, previous):
        if item:
            if not self.currentLayer.criDBName == item.text():
                self.currentLayer.criDBName = item.text()
                self.layerNameField.setText(item.text())
                self.on_layerNameField_editingFinished()
                self.dirty = True
                self.updateStatus("changed database entry for {} to {}".format(
                                           self.currentLayer.name, item.text()))

    @pyqtSlot(int)
    def on_sroughThicknessEdit_valueChanged(self, value):
        if not self.currentLayer.sroughThickness == value:
            self.currentLayer.sroughThickness = value
            self.dirty = True
            self.updateStatus("changed roughness thickness for {} to {}".format(
                                       self.currentLayer.name, str(value)))
        
    @pyqtSlot(bool)
    def on_constantPointsRB_toggled(self, checked):
        if checked and not self.currentLayer.mesh['meshing'] == 0:
            self.setMeshing()
            self.dirty = True
            self.updateStatus("changed meshing for {} to constant number of points.".format(self.currentLayer.name))
        
    @pyqtSlot(bool)
    def on_constantDistRB_toggled(self, checked):
        if checked and not self.currentLayer.mesh['meshing'] == 1:
            self.setMeshing()
            self.dirty = True
            self.updateStatus("changed meshing for {} to constant depth steps.".format(self.currentLayer.name))
    
    @pyqtSlot(bool)
    def on_autoDistRB_toggled(self, checked):
        if checked and not self.currentLayer.mesh['meshing'] == 2:
            self.setMeshing()
            self.dirty = True
            self.updateStatus("changed meshing for {} to automatic.".format(self.currentLayer.name))
    
    @pyqtSlot(int)
    def on_constantPointsSB_valueChanged(self, p0):
        if not self.currentLayer.mesh['Points'] == p0:
            self.currentLayer.mesh['Points'] = p0
            self.currentLayer.makeXnodes()
            self.currentLayer.makeXcollection()
            self.currentLayer.makeXgrading()
            self.updateMeshPoints()
            self.dirty = True
            self.updateStatus("changed number of constant meshing points for {} to {}.".format(self.currentLayer.name, p0))
    
    @pyqtSlot(int)
    def on_constantDistSB_valueChanged(self, p0):
        if not self.currentLayer.mesh['Dist'] == p0:
            self.currentLayer.mesh['Dist'] = p0
            self.currentLayer.makeXnodes()
            self.currentLayer.makeXcollection()
            self.currentLayer.makeXgrading()
            self.updateMeshPoints()
            self.dirty = True
            self.updateStatus("changed constant depth step for meshing of {} to {}.".format(self.currentLayer.name, p0))
    
    def setMeshing(self):
        if self.constantPointsRB.isChecked():
            self.currentLayer.mesh['meshing'] = 0
        elif self.constantDistRB.isChecked():
            self.currentLayer.mesh['meshing'] = 1
        else:
            self.currentLayer.mesh['meshing'] = 2
        self.currentLayer.makeXnodes()
        self.currentLayer.makeXcollection()
        self.currentLayer.makeXgrading()
        self.updateMeshPoints()
    
    def updateMeshPoints(self):
        currPoints = len(self.currentLayer.x)
        stackPoints = 0
        for layer in self.stack:
            stackPoints += len(layer.x)
        self.meshLabel.setText('number of mesh points current layer: %i\n\nnumber of mesh points complete stack: %i' %(currPoints, stackPoints))
        
    def getCRI(self, layer):
        fName = ''
        wvl = self.settings['wavelength']
        if layer.criSource == 'from database':
            fName = self.MaterialDB[layer.criDBName]
        elif layer.criSource == 'from file':
            fName = layer.criFile['path']
            if layer.criFile['alpha']:
                w, k = self.criLoadAlphaFile(fName)
                layer.n = np.ones(len(w)) * self.criFileSpinBox.value()
                layer.k = k
                layer.wavelength = w
                return
        elif layer.criSource == 'constant':
            n = layer.criConstant[0]
            k = layer.criConstant[1]
            layer.wavelength = wvl
            layer.n = np.ones(len(wvl)) * n
            layer.k = np.ones(len(wvl)) * k
            return
        elif layer.criSource == 'dielectric function':
            layer.n = layer.dielectricFunction['n'][::-1]
            layer.k = layer.dielectricFunction['k'][::-1]
            layer.wavelength =  layer.dielectricFunction['wvl'][::-1]
            return
            
        elif layer.criSource == 'graded':
            layer.criGrading['xMoles'] = []
            layer.criGrading['Egs'] = []
            layer.criGrading['n_idc'] = []
            layer.criGrading['k_idc'] = []
            for file in layer.criGrading['files']:
                w, n, k = self.criLoadFile(file[2])
                if w[0] > wvl[0] or w[-1] < wvl[-1]:
                    self.warning('The cri file of {} does no cover the specified wavelength range'.format(layer.name))
                n = np.interp(wvl, w, n)
                k = np.interp(wvl, w, k)
                layer.criGrading['xMoles'].append(file[0])
                layer.criGrading['Egs'].append(file[1])
                layer.criGrading['n_idc'].append(n) 
                layer.criGrading['k_idc'].append(k)
            # set first file values to defaults for plot when "show optical constants" is clicked
            layer.wavelength = wvl
            layer.n = layer.criGrading['n_idc'][0]
            layer.k = layer.criGrading['k_idc'][0]
            return
            
        if fName:
            w, n, k = self.criLoadFile(fName)
            if w[0] > wvl[0] or w[-1] < wvl[-1]:
                    self.warning('The cri file of {} does no cover the specified wavelength range'.format(layer.name))
            layer.wavelength = w
            layer.n = n
            layer.k = k
        else:
            raise LoadError("There is no cri file path for {} defined!".format(layer.name))


    def criLoadFile(self, filename):
        """opens and read cri files
        File structure:
        column 1 -- wavelength (nm)
        column 2 -- n
        column 3 -- k
        """
        w = []
        n = []
        k = []
        wvl_factor = 1
        ln = 1
        try:
            f = open(filename)
            while True:
                line = f.readline()
                if not line:
                    break
                if '[mum]' in line:
                    wvl_factor = 1000
                if line[0].isdigit():
                    fields = line.split("\t")
                    if len(fields) != 3:
                        raise LoadError("Line {}:\nFile {} has wrong column format!\nShould be:\n[wvl]\t[n]\t[k]".format(ln, filename))
                    w.append(num(fields[0]) * wvl_factor)
                    n.append(num(fields[1]))
                    k.append(num(fields[2]))
                ln += 1
            return w, n, k
            f.close()
        except IOError as e:
            raise LoadError("Could not read file {}: \n {}".format(filename, e.args[1]))
    
    def criLoadAlphaFile(self, filename):
        w_list = []
        k_list = []
        wvl_factor = 1
        alpha_factor = 1
        ln = 1
        try:
            f = open(filename)
            while True:
                line = f.readline()
                if not line:
                    break
                if '[mum]' in line:
                    wvl_factor = 1000
                if 'cm^-1' in line or '1/cm' in line:
                    alpha_factor = 1e-7 # --> nm^-1
                else:# 'm^-1' in line or '1/m' in line: default
                    alpha_factor = 1e-9 # --> nm^-1
                if line[0].isdigit():
                    fields = line.split("\t")
                    if len(fields) != 2:
                        raise LoadError("Line {}:\nFile {} has wrong column format!\nShould be:\n[wvl]\t[alpha]".format(ln, filename))
                    w = num(fields[0]) * wvl_factor
                    k = num(fields[1]) * alpha_factor * w / (4 * np.pi) # k = alpha*Lambda/4pi
                    w_list.append(w)
                    k_list.append(k)
                ln += 1
            return w_list, k_list
            f.close()
        except IOError as e:
            raise LoadError("Could not read file {}: \n {}".format(filename, e.args[1]))

    def loadMaterialDB(self):
        '''
        look for files in directory MaterialDB
        create a dictionary with Materialnames and corresponding absolute path
        '''
        #TODO: check differen cwd at other os
        path = self.settings['MaterialDBPath']
        if not os.path.isdir(path):
            self.warning('Path to material database does not exist! Default directory is choosen. Some of your definitions may be changed.')
            path = os.getcwd() + "\\materialDB"
        included_extenstions = ['dat']
        self.MaterialFiles = [fn for fn in os.listdir(path) if any([fn.endswith(ext) for ext in included_extenstions])]
        self.Materials = []
        for i, Mat in enumerate(self.MaterialFiles):
            self.Materials.append(Mat.replace('.dat', ''))
        criFilePaths = [(self.settings['MaterialDBPath'] + '\\' + i) for i in self.MaterialFiles]
        self.MaterialDB = dict(zip(self.Materials,  criFilePaths))
        self.criDBList.clear()
        self.criDBList.addItems(sorted(self.Materials))
   
    def runStack(self):
        startTime = time.time()
        self.StackName = self.checkStackName(self.StackNameEdit.text())
        try:
            currentOptics = self.simulate()
        except LoadError as e:
            logging.exception("There was a problem with loading a file.")
            logging.info('simulation stopped due to error')
            logging.shutdown()
            self.warning(e.msg)
            return
        except OutOfRangeError as r:
            self.warning(r.msg)
            logging.exception("There was a problem with loading a file.")
            logging.info('simulation stopped due to error')
            logging.shutdown()
            return
        except WriteError as e:
            self.warning(e.msg)
            logging.exception("There was a problem with writing a file.")
            logging.info('simulation stopped due to error')
            logging.shutdown()
            return 
        except:
            logging.exception("There was an unknown error:")
            logging.info('simulation stopped due to error')
            logging.shutdown()
            raise
            return
        #currentOptics.createReferenceCurves(self.references)
        #--------------------------
        #--- Plot major results ---
        if self.defaults['plots']:
            logging.info('create some plots...')
        for plot in self.defaults['plots']:
            if plot == 0: # stack optics
                toPlot = currentOptics.availablePlots['spectra']['total A,R,T']
                title = 'total A,R,T ({})'.format(self.StackName)
                xRange = self.settings['wavelength']
                xLabel = 'wavelength (nm)'
                yLabel = 'total A,R,T'
                PlotSubw = Subwindow(title, xRange, toPlot, xLabel, yLabel)
                self.mdiArea.addSubWindow(PlotSubw)
                PlotSubw.show()
            if plot == 1: # E-Field
                toPlot = currentOptics.availablePlots['profiles']['E-field intensity']
                title = 'E-field intensity ({})'.format(self.StackName)
                xRange = currentOptics.x
                xLabel = 'depth (nm)'
                yLabel = 'E-field intensity'
                PlotSubw = Subwindow(title, xRange, toPlot, xLabel, yLabel)
                self.mdiArea.addSubWindow(PlotSubw)
                PlotSubw.show()
            if plot == 2: # layerwise optics
                toPlot = currentOptics.availablePlots['spectra']['absorption (layerwise)']
                title = 'layerwise absorption ({})'.format(self.StackName)
                xRange = self.settings['wavelength']
                xLabel = 'wavelength (nm)'
                yLabel = 'absorption'
                PlotSubw = Subwindow(title, xRange, toPlot, xLabel, yLabel)
                self.mdiArea.addSubWindow(PlotSubw)
                PlotSubw.show()
            if plot == 3: # layerwise optics
                toPlot = currentOptics.availablePlots['spectra']['QE']
                title = 'QE ({})'.format(self.StackName)
                xRange = self.settings['wavelength']
                xLabel = 'wavelength (nm)'
                yLabel = 'quantum efficiency'
                PlotSubw = Subwindow(title, xRange, toPlot, xLabel, yLabel)
                self.mdiArea.addSubWindow(PlotSubw)
                PlotSubw.show()
            if plot == 4: # generation
                toPlot = currentOptics.availablePlots['profiles']['generation']
                title = 'generation ({})'.format(self.StackName)
                xRange = currentOptics.x
                xLabel = 'depth (nm)'
                yLabel = 'optical and collected generation'
                PlotSubw = Subwindow(title, xRange, toPlot, xLabel, yLabel)
                self.mdiArea.addSubWindow(PlotSubw)
                PlotSubw.show()
            if plot == 5: # Ellipsometry
                toPlot = currentOptics.availablePlots['spectra']['Ellipsometry']
                title = 'SE ({})'.format(self.StackName)
                xRange = self.settings['wavelength']
                xLabel = 'wavelength (nm)'
                yLabel = 'psi / delta'
                PlotSubw = Subwindow(title, xRange, toPlot, xLabel, yLabel)
                self.mdiArea.addSubWindow(PlotSubw)
                PlotSubw.show()
                
            if plot == 6: # Lambert Beer
                toPlot = currentOptics.availablePlots['spectra']['QE']
                title = 'EQE LB ({})'.format(self.StackName)
                xRange = self.settings['wavelength']
                xLabel = 'wavelength (nm)'
                yLabel = 'EQE'
                PlotSubw = Subwindow(title, xRange, toPlot, xLabel, yLabel)
                self.mdiArea.addSubWindow(PlotSubw)
                PlotSubw.show()
        self.mdiArea.tileSubWindows()
        
        # pass calulation results to result list and resultmodellist
        self.addResult(currentOptics)
        
        self.onProgress(100)
        totalTime = time.time() - startTime 
        self.updateStatus('calculation completed successfully in %.2f s' % totalTime)
        
        logging.info(strings.endLog(totalTime))
        
        self.onProgress(0)
        self.stopLogging()
        
    def simulate(self):
        self.startLogging()
            
        #try:
        input = LayerStack(self.StackName, self.stack, self.settings, self.getCRI)
        #except LoadError as e:
            
           # raise LoadError(e)
            
        startCalcTime = time.time() 
        
        self.updateStatus('calculate stack optics')
        logging.info('\ncalculate optics...\n')
        
        currentOptics = Optics(self.StackName, input, self.references, self.settings)
        currentOptics.createReferenceCurves()
        self.onProgress(10)
        
        length = len(self.defaults['calculations'])
        
        # ------------ What to calculate? --------
        if 0 in self.defaults['calculations']:
            currentOptics.calcStack()
            self.onProgress((100 * 1 / length) - 10)
        if 1 in self.defaults['calculations']:
            currentOptics.calcFieldIntensity()# requires calcStack
            self.onProgress((100 * 2 / length) - 10)
        if 2 in self.defaults['calculations']:
            currentOptics.calcAbsorption()# requires Field intensity
            self.onProgress((100 * 3 / length) - 10)
        if 3 in self.defaults['calculations']:
            currentOptics.calcQE()# requires Layerwise optics
            self.onProgress((100 * 4 / length) - 10)        
        if 4 in self.defaults['calculations']:
            currentOptics.calcGeneration()# requires Layerwise optics
            self.onProgress((100 * 5 / length) - 10)        
        if 5 in self.defaults['calculations']:
            currentOptics.calcEllipsometry()
        if 6 in self.defaults['calculations']:
            currentOptics.calcOptBeamTotal()
            
        endCalcTime = time.time()
        currentOptics.scalars['calc. time (s)'] = endCalcTime - startCalcTime
        
        logging.info('\n... optics calculated in {:.4f} s.\n'.format(currentOptics.scalars['calc. time (s)']))
        return currentOptics
        
    def defineBatch(self):
        variables = BatchDlg(self.stack, self.batchVariables, self)
        if variables.exec_():
            self.batchVariables = variables.variables
    
    def runBatch(self):
        if self.batchVariables:
            for variable in self.batchVariables:
                if variable[0] == 0:
                    # case of layer parametervariation
                    #print(variable[1])
                    for i, layer in enumerate(self.stack):
                        if layer.name == variable[1]:
                            stackIndex = i
                            NamePart = layer.name
                    self.createStackView(stackIndex)
                    if variable[2] == 'thickness':
                        parameter = 'self.on_layerThicknessSB_valueChanged(value)'
                        NamePart = NamePart + ' t = '
                    elif variable[2] == 'roughness' and self.stack[stackIndex].srough == True:
                        parameter = 'self.on_sroughThicknessEdit_valueChanged(value)'#'self.stack[stackIndex].sroughThickness'
                        NamePart = NamePart + ' rough t = '
                    elif variable[2] == 'Haze R' and self.stack[stackIndex].srough == True:
                        parameter = 'self.on_hazeRSlider_valueChanged(value)'#'self.stack[stackIndex].sroughThickness'
                        NamePart = NamePart + ' rough t = '
                    elif variable[2] == 'Haze T' and self.stack[stackIndex].srough == True:
                        parameter = 'self.on_Ha_valueChanged(value)'#'self.stack[stackIndex].sroughThickness'
                        NamePart = NamePart + ' rough t = '
                    elif variable[2] == 'constant n' and self.stack[stackIndex].criSource == 'constant':
                        parameter = 'self.on_criConstantnEdit_valueChanged(value)'#'self.stack[stackIndex].criConstant[0]'
                        NamePart = NamePart + ' n = '
                    elif variable[2] == 'constant k' and self.stack[stackIndex].criSource == 'constant':
                        parameter = 'self.on_criConstantkEdit_valueChanged(value)'
                        NamePart = NamePart + ' n = '
                    elif variable[2] == 'diffusion length' and self.stack[stackIndex].collection['source'] == 'from diffusion length':
                        parameter = 'self.on_diffLengthSB_valueChanged(value)'
                        NamePart = NamePart + ' D_l = '
                    else:
                        break
                        
                elif variable:
                    # case of layer stack variation
                    if variable[1] == 'excitation':
                       if variable[2] == 'angle of incidence':
                            parameter = 'self.settings[\'angle\'] = value'
                            NamePart = ' angle = '
                else:
                    break
                    
                for value in np.arange(variable[3][0], variable[3][2]+variable[3][1], variable[3][1]):
                    self.StackName = self.StackNameEdit.text() + ' ' + NamePart + ' ' + str(value)
                    exec(parameter)
                    currentOptics = self.simulate()
                    self.addResult(currentOptics)
                    
            self.onProgress(100)
            
            self.updateStatus('all batch simulations successfully done')
            
            self.onProgress(0)
        
    def fitThickness(self):
        #TODO: Nealder-Mead method?
        fitting = FittingThicknessDlg(self.stack, self.references, self)
        
        if fitting.exec_():
            if not self.resultlist:
                self.warning('There should be at least one successful calcluation of the stack!')
                return
            self.startLogging()
            logging.info('start fitting routine (thickness)...')
            self.layerToFit = fitting.selectedLayer
            t = self.stack[self.layerToFit].thickness
            xdata = self.settings['wavelength']
            # get ydata from referenceFile
            self.referenceToFit = fitting.selectedReference
            path = self.references[self.referenceToFit][0] 
            if path is not '':
                try:
                    rawdata = np.loadtxt(path, comments='#')
                except IOError as e:
                    raise LoadError('Could not open {} file: \n {}'.format(name, e.args[1]))
                try:
                    data = np.interp(xdata, rawdata[:, 0], rawdata[:, 1])
                except: 
                    raise LoadError('Could not interpolate {} file: \n to given spectrum'.format(name))
                if data.mean() > 1: # check if given in %
                    data = data / 100
            else:
                self.warning('No reference data found!')
                return
            ydata = data
            # curve fitting (func, xdata, ydata, p0,
            self.noOfFitIterations = 0
            self.updateStatus('busy fitting ...')
            
            try:
                #fitParams, fitCovariances = curve_fit(self.fitThicknessFunction, xdata, ydata, t, jac='3-point',  diff_step=0.01, method='trf', bounds=(0, 5000), max_nfev=fitting.noOfIterations)# , sigma=2,  epsfcn = -0.01,
                minResult = minimize(self.fitThicknessFunctionMinimize, t, args = (xdata, ydata), method= fitting.method, options = {'maxiter' : fitting.noOfIterations}) #, tol=1e-6
                #minResult = basinhopping(self.fitThicknessFunctionMinimize, t, minimizer_kwargs={'args': (xdata, ydata), 'method': fitting.method}, niter=10, stepsize = 20)
                #minResult = minimize_scalar(self.fitThicknessFunctionMinimize, args = (xdata, ydata), method= 'Bounded', bounds=(500, 1000))
            except RuntimeError as e:
                QtWidgets.QMessageBox.warning(self,
                    "fitting error",
                    'Error - curve fitting failed!\n{}'.format(e.args[0]),
                    QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Close))
                return
            self.updateStatus('Fitting requires {} iterations'.format(self.noOfFitIterations))
            
            #QtWidgets.QMessageBox.information(self,
              #      "Fitting result",
                #    'The optimized layer thickness of {} is {}.\n Covariances are {}'.format(self.stack[self.layerToFit].name, fitParams, fitCovariances),
                  #  QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Close))
            message = """The optimized layer thickness of {} is {:.2f} nm.\n
            Details: {}\n
            Number of Iterations: {}\n
            Number of function calls: {}\n
            Chi-square: {:7.4f}""".format(self.stack[self.layerToFit].name, minResult.x[0], minResult.message, minResult.nit, minResult.nfev, minResult.fun)
            
            logging.info('\n' + 50 * '#' + '\n' + message + '\n do final calculation ...\n' + 50 * '#')
                        
            QtWidgets.QMessageBox.information(self, "Fitting result",message, QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Close))#,minResult.message
            self.ShowLayerDetails()
            # plot result
            toPlot = dict([('fit', self.fitThicknessFunction(xdata, minResult.x)),
                            ('{}'.format(self.referenceToFit), ydata)])
            title = 'Fitting result'
            xRange = self.settings['wavelength']
            xLabel = 'wavelength (nm)'
            yLabel = self.referenceToFit
            PlotSubw = Subwindow(title, xRange, toPlot, xLabel, yLabel)
            self.mdiArea.addSubWindow(PlotSubw)
            PlotSubw.show()
            
            #print(minResult.fun)
            logging.info('Fitting finished.')
            self.stopLogging()
            
            
    def fitThicknessFunction(self, xdata, t):
        #print(t)
        self.noOfFitIterations += 1
        self.stack[self.layerToFit].thickness = t
        input = LayerStack(self.StackName, self.stack, self.settings, self.getCRI)   
        self.StackName = self.checkStackName(self.StackNameEdit.text())
        optics = Optics(self.StackName, input, self.references, self.settings)
        optics.calcStack()
        if 'R' in self.referenceToFit:
            return optics.RspectrumSystem
        elif 'T' in self.referenceToFit:
            return optics.TspectrumSystem
        elif 'EQE' in self.referenceToFit:
            optics.calcFieldIntensity()
            optics.calcAbsorption()
            optics.calcQE()
            return optics.EQE
        elif 'psi' in self.referenceToFit:
            optics.calcEllipsometry()
            return optics.psi
        elif 'delta' in self.referenceToFit:
            optics.calcEllipsometry()
            return optics.delta
        
    def fitThicknessFunctionMinimize(self, t, xdata, ydata):
        #print(t)
        self.noOfFitIterations += 1
        self.stack[self.layerToFit].thickness = t
        input = LayerStack(self.StackName, self.stack, self.settings, self.getCRI)   
        self.StackName = self.checkStackName(self.StackNameEdit.text())
        optics = Optics(self.StackName, input, self.references, self.settings)
        #optics.createReferenceCurves() #not needed
        optics.calcStack()
        if 'R' in self.referenceToFit:
            ref = optics.RspectrumSystem
        elif 'T' in self.referenceToFit:
            ref = optics.TspectrumSystem
        elif 'EQE' in self.referenceToFit:
            optics.calcFieldIntensity()
            optics.calcAbsorption()
            optics.calcQE()
            ref = optics.EQE
        elif 'psi' in self.referenceToFit:
            optics.calcEllipsometry()
            ref = optics.psi
        elif 'delta' in self.referenceToFit:
            optics.calcEllipsometry()
            ref = optics.delta
        return np.sum((((ref - ydata)/ydata))**2) 
        
    def fitDiffLength(self):
        fitting = FittingDiffusion(self.stack, self.references, self)
        if fitting.exec_():
            if not self.resultlist:
                self.warning('There should be at least one successful calcluation of the stack!')
                return
            self.startLogging()
            logging.info('start fitting routine (diffusion length) ...')
            self.layerToFit = fitting.selectedLayer
            diffL = self.stack[self.layerToFit].collection['diffLength']
            #print(diffL)
            xdata = self.settings['wavelength']
            # get ydata from referenceFile
            self.referenceToFit = fitting.selectedReference
            path = self.references[self.referenceToFit][0] 
            if path is not '':
                try:
                    rawdata = np.loadtxt(path, comments='#')
                except IOError as e:
                    self.warning('Could not open {} file: \n {}'.format(path, e.args[1]))
                    return
                try:
                    data = np.interp(xdata, rawdata[:, 0], rawdata[:, 1])
                except: 
                    self.warning('Could not interpolate {} file: \n to given spectrum'.format(name))
                    return
                if data.mean() > 1: # check if given in %
                    data = data / 100
            else:
                self.warning('No reference data found!')
                return
            ydata = data
            # curve fitting (func, xdata, ydata, p0,
            self.noOfFitIterations = 0
            self.updateStatus('busy fitting ...')
            try:
                #fitParams, fitCovariances = curve_fit(self.fitDiffLengthFunction, xdata, ydata, diffL, method='trf', bounds=(100, 4000), diff_step=100, max_nfev=fitting.noOfIterations) #ftol = 0.0001 factor=20, epsfcn = -0.01, 
                minResult = minimize(self.fitDiffLengthFunctionMinimize, diffL, args = (xdata, ydata), method= fitting.method, options = {'maxiter' : fitting.noOfIterations}) #, tol=1e-6
                
            except RuntimeError as e:
                QtWidgets.QMessageBox.warning(self,
                    "fitting error",
                    'Error - curve fitting failed!\n{}'.format(e.args[0]),
                    QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Close))
                return
            self.updateStatus('Fitting requires {} iterations'.format(self.noOfFitIterations))
            
            message = """The optimized diffusion length of {} is {:7.2f} nm.\n
            Details: {}\n
            Number of Iterations: {}\n
            Number of function calls: {}\n
            Chi-square: {:7.4f}""".format(self.stack[self.layerToFit].name, minResult.x[0], minResult.message, minResult.nit, minResult.nfev, minResult.fun)
            
            logging.info('\n' + 50 * '#' + '\n' + message + '\n do final calculation ...\n' + 50 * '#')
            
            QtWidgets.QMessageBox.information(self, "Fitting result", message, QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Close))
            
            self.ShowLayerDetails()
            # plot result
            toPlot = dict([('fit', self.fitDiffLengthFunction(xdata, minResult.x)),
                            ('{}'.format(self.referenceToFit), ydata)])
            title = 'Fitting result'
            xRange = self.settings['wavelength']
            xLabel = 'wavelength (nm)'
            yLabel = self.referenceToFit
            PlotSubw = Subwindow(title, xRange, toPlot, xLabel, yLabel)
            self.mdiArea.addSubWindow(PlotSubw)
            PlotSubw.show()
            
            logging.info('Fitting finished.')
            self.stopLogging()
            
        
    def fitDiffLengthFunction(self, xdata, diffL):
        #print(diffL)
        self.noOfFitIterations += 1
        self.stack[self.layerToFit].collection['diffLength'] = diffL
        input = LayerStack(self.StackName,  self.stack, self.settings, self.getCRI)   
        #self.StackName = self.checkStackName(self.StackNameEdit.text())
        optics = Optics(self.StackName, input, self.references, self.settings)
        optics.calcStack()
        optics.calcFieldIntensity()
        optics.calcAbsorption()
        optics.calcQE()
        return optics.EQE
        
    def fitDiffLengthFunctionMinimize(self, diffL, xdata, ydata):
        #print(diffL)
        self.noOfFitIterations += 1
        self.stack[self.layerToFit].collection['diffLength'] = diffL
        self.stack[self.layerToFit].makeXcollection()
        self.plotCollectionFunction()
        input = LayerStack(self.StackName,  self.stack, self.settings, self.getCRI)   
        #self.StackName = self.checkStackName(self.StackNameEdit.text())
        optics = Optics(self.StackName, input, self.references, self.settings)
        optics.calcStack()
        optics.calcFieldIntensity()
        optics.calcAbsorption()
        optics.calcQE()
        ref = optics.EQE
        result = np.sum(((ref - ydata)/ydata)**2) 
        #print(result)
        return result
        
    def fitAdvanced(self):
        fitting = FittingAdvancedDlg(self.stack, self.references, self.StackNameEdit.text(), self.settings, self.getCRI,self)
        
        if fitting.exec_():
            self.stack = fitting.stack
            self.createStackView(self.selectedLayer)
            
            
        
    def addResult(self, currentresult):
        self.resultlist.append(currentresult)
        
        row = self.resultmodel.rowCount()
        self.resultmodel.beginResetModel()
        self.resultmodel.stacks.append(currentresult)
        self.resultmodel.LabelList = self.defaults['scalars'] 
        self.resultmodel.endResetModel()
        index = self.resultmodel.index(row, 0)
        self.ResultTableView.setCurrentIndex(index)
        self.ResultTableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def checkStackName(self, Name):
        if Name in self.resultNames:
            self.resultNames[Name] = self.resultNames[Name] + 1
            return Name + '_{}'.format(self.resultNames[Name])
        else:
            self.resultNames[Name] = 0
            return Name


    def createMdiChild(self):
        subw = Subwindow('no name')
        self.mdiArea.addSubWindow(subw)
        return subw
    
    
    @pyqtSlot()
    def on_showCRI_clicked(self):
        """
        Slot documentation goes here.
        """
        try:
            self.getCRI(self.currentLayer)
        except LoadError as e:
            self.warning(e.msg)
            return
        if self.currentLayer.criSource == 'graded':
            toPlot = {}
            for i, xMole in enumerate(self.currentLayer.criGrading['xMoles']):
                toPlot['n at xMole = %.2f' % xMole] = self.currentLayer.criGrading['n_idc'][i]
                toPlot['k at xMole = %.2f' % xMole] = self.currentLayer.criGrading['k_idc'][i]
        else:
            toPlot = {'n': self.currentLayer.n, 'k': self.currentLayer.k}
        CRIsubw = Subwindow('nk plot ' + self.currentLayer.name,
            self.currentLayer.wavelength,toPlot,
            'wavelength', 
            'complex refractive index (nm)')
        self.mdiArea.addSubWindow(CRIsubw)
        CRIsubw.show()
            #self.mpl.canvas.mpl_connect('pick_event', self.on_pick)


    def showAllCRI(self):
        """
        Creates subwindow and plots all cri of the stack
        """
        
        plotDict = {}
        wvl = self.settings['wavelength']
        for currentLayer in self.stack:
            try:
                self.getCRI(currentLayer)
            except LoadError as e:
                self.warning(e.msg)
                return
            if currentLayer.criSource == 'constant':
                n = currentLayer.n
                k = currentLayer.k
            else:
                n = np.interp(wvl, currentLayer.wavelength, currentLayer.n)
                k = np.interp(wvl, currentLayer.wavelength, currentLayer.k)
            plotDict['n ' + currentLayer.name] = n
            plotDict['k '+ currentLayer.name] = k
                
        #TODO: varying modification needs to be implemented, now interpolated to self.wavelength
        CRIsubw = Subwindow('nk plot for all layers',
                wvl,
                plotDict,
                'wavelength (nm)', 
                'complex refractive index')
        self.mdiArea.addSubWindow(CRIsubw)
        CRIsubw.show()    

    def updateWindowMenu(self):
        self.windowMenu.clear()
        windows = self.mdiArea.subWindowList()
        
        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.windowTitle())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(window is self.mdiArea.activeSubWindow())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)
        
        self.addActions(self.windowMenu, (None, self.windowCascadeAction,
                self.windowTileAction, self.windowRestoreAction,
                self.windowMinimizeAction, self.windowCloseAction))
    

    def windowRestoreAll(self):
        for window in self.mdiArea.subWindowList():
            window.showNormal()


    def windowMinimizeAll(self):
        for window in self.mdiArea.subWindowList():
            window.showMinimized()


    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)
            
    
    
    @pyqtSlot(QtWidgets.QMdiSubWindow)
    def on_mdiArea_subWindowActivated(self, p0):
        SubW = self.mdiArea.activeSubWindow()
        
        if SubW:
            
            self.PlotToolBar.clear()
            #Handlers = QtGui.QWidget()
            
            self.ntb = NavigationToolbar(SubW.widget().canvas, self)
            self.PlotToolBar.addWidget(self.ntb)            
            #SubW.widget().dataTable.addAction(self.saveDataAction)
            #SubW.widget().dataTable.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
        else:
            self.PlotToolBar.clear()
            
        #TODO: insert function to add curve from file, or drag-drop from curvelist
        
    def saveAsStack(self):
        if not self.stack:
            return
        fName = self.fileName if self.fileName is not None else self.StackNameEdit.text()
        fName, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Stack to file', fName,'stack files (*.mop)')
        if fName:
            self.fileName = fName
            self.saveStack()
            self.addRecentFile(fName)
    
    def saveStack(self):
        '''
        '''
        if not self.stack:
            return
        if self.fileName is None:
            self.saveAsStack()
        else:
            
            file = open(self.fileName, 'wb')
            p = pickle.Pickler(file)
            p.dump(__version__)
            p.dump(self.StackNameEdit.text())
            p.dump(self.settings)
            p.dump(self.defaults)
            p.dump(self.references)
            p.dump(len(self.stack))
            for element in self.stack:
                p.dump(element)               
            file.close()
            self.dirty = False
            self.updateStatus("Saved as {}".format(self.fileName))

    def openStack(self):
        if not self.okToContinue():
            return
        dir = (os.path.dirname(self.fileName)
               if self.fileName is not None else "./stacks")
        fName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 
                    'Open Stack from file', dir, 'stack files (*.mop)')
        if fName:
            try:
                self.loadStack(fName)
            except LoadError as e:
                self.warning(e.msg)
                
    def loadStack(self, fName = None):
        '''
        '''
        if fName is None:
            #get fName from recentFiles action's data value
            action = self.sender()
            if isinstance(action, QtWidgets.QAction):
                fName = action.data()
                if not self.okToContinue():
                    return
            else:
                return
        if fName:
            try:
                file = open(fName, 'rb')
                u = pickle.Unpickler(file)
                fileVersion = u.load()
                self.stack=[]
                self.StackNameEdit.setText(u.load())
                self.settings = u.load()
                # check if path of materialDB is available on machine
                if not os.path.isdir(self.settings['MaterialDBPath']):
                    self.warning('Could not find path of material data base: {}\nPlease select correct directory.'.format(self.settings['MaterialDBPath']))
                    DirName = QtWidgets.QFileDialog.getExistingDirectory(self, 'select a folder containing the nk files', os.getcwd()+'\\materialDB')
                    if DirName:
                        self.settings['MaterialDBPath'] = DirName
                    else:
                        self.settings['MaterialDBPath'] = os.getcwd()+'\\materialDB'
                self.loadMaterialDB()
                self.defaults = u.load()
                self.references = u.load()
                lenStack = u.load()
                for i in range(lenStack):
                    layer = u.load()
                    self.stack.append(layer)
                    # check for database entry
                    if layer.criDBName not in self.Materials:
                        self.warning('There is no DB entry for layer {}! Changed to {}.'.format(layer.name, self.Materials[0]))
                        layer.criDBName = self.Materials[0]
        
                #self.stack.append(loadedStack)
                self.createStackView(0)
                file.close()
                
                self.fillSimulationOptions()
                
                self.fileName = fName
                self.lastFile = fName
                self.addRecentFile(fName)
                message = "Loaded {}".format(os.path.basename(fName))
                self.dirty = False
                self.updateStatus(message)
            except:
                raise LoadError("Could not load file {} for stack setup!\n"\
                                "Check for correct Version:\nthis program version: {}\tfile version: {}\n{}".format(fName, __version__, fileVersion, sys.exc_info()[1]))

            
    def saveData(self):
        SubW = self.mdiArea.activeSubWindow()
        
        if SubW:
            try:
                self.mdiArea.activeSubWindow().widget().saveData()
            except WriteError as e:
                self.warning(e.msg)
        else:
            self.updateStatus('There is no curve data selected!')    
            
    def showColor(self):
        if self.resultlist:
            color = ColorDlg(self.resultlist, self)
            color.exec_()
            pass
        else:
            self.updateStatus('no results found!')
            
    def showLogFile(self):
        Dlg = QtWidgets.QDialog(self)
        layout = QtWidgets.QHBoxLayout()
        TextEdit = QtWidgets.QTextEdit()
        TextEdit.setReadOnly(True)
        TextEdit.setStyleSheet("font: 9pt \"Courier\";")
        layout.addWidget(TextEdit)
        Dlg.setLayout(layout)
        Dlg.setMinimumWidth(800)
        Dlg.setMinimumHeight(800)
        Dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        text=open('LogFile.log').read()
        TextEdit.setPlainText(text)
        Dlg.exec_()
        
    def saveSCAPSGenerationEnable(self):
        if len(self.selectedRows) == 1:
            result = self.resultlist[self.selectedRows[0]]
            if 'generation' in result.availablePlots['profiles']:
                self.saveSCAPSGenerationAction.setEnabled(True)
            else:
                self.saveSCAPSGenerationAction.setEnabled(False)
        else:
            self.saveSCAPSGenerationAction.setEnabled(False)
        
    def saveSCAPSGeneration(self):
        gen = self.resultlist[self.selectedRows[0]].availablePlots['profiles']['generation']['optical generation (1/cm³s)'][::-1]
        gen = np.array(gen, dtype= 'float64') * 1000000 # 1/cm^3.s --> 1/m^3.s
        x = self.resultlist[self.selectedRows[0]].x[::-1] / 1000
        x = np.abs(x-x[0])
        spectrum = self.resultlist[self.selectedRows[0]].spectrumFile
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save generation profile to file', '','data files (*.gen)')
        if fname:
            #try:
            f = open(fname, 'w')
            f.write('< generation profile calculated with OptiSim Version {}\n<\n<spectrum: {}\n<illumination from right\n<Distance from backcontact (um)\t Generation (#//m^3.s)\n'.format(__version__, spectrum))
            for i in range(len(x)):
                f.write(str(x[i]) + '\t' + str(gen[i]) + '\n')
            f.close()
            #except IOError as e:
            #    self.warning("Could not write data to file {}: \n {}".format(fname, e.args[1]))
            #except:
                #self.warning("Could not write data to file {}: \n {}".format(fname, e.args[1]))
            #    print('OtherError')
                #self.warning("Could not write data to file {}: \n {}".format(fname, e.args[1]))
        
    def fillCurveList(self, currentlySelected, deselected):
        self.selectedRows = []
        selected = self.ResultTableView.selectionModel().selectedRows()
        self.CurveTreeWidget.clear()
        if len(selected) > 0:
            for index in selected:
                    self.selectedRows.append(index.row())
            result = self.resultlist[self.selectedRows[0]]
            notToShow = []
            CurveDict = result.availablePlots.copy()
            
            if len(self.selectedRows) > 1:
                for row in self.selectedRows:
                    result = self.resultlist[row]
                    for root in list(CurveDict.keys()):
                        for category in list(CurveDict[root].keys()):
                            if category not in result.availablePlots[root].keys():
                                notToShow.append(category)
                                #del CurveDict[root][category]
                                continue
                            if root == '2D':
                                continue
                            for plot in list(CurveDict[root][category].keys()):
                                if plot not in result.availablePlots[root][category].keys():
                                    notToShow.append(plot)
                                    #del CurveDict[root][category][plot]
                                    #CurveDict[root][category].pop(plot, None)
                    
            # populate TreeWidget
            self.CurveTreeWidget.setColumnCount(1)
            
            for root in sorted(CurveDict.keys(), reverse=True):
                rootItem = QtWidgets.QTreeWidgetItem()
                rootItem.setText(0, root)
                self.CurveTreeWidget.addTopLevelItem(rootItem)
                
                for category in sorted(CurveDict[root].keys()):
                    if category not in notToShow:
                        catItem = QtWidgets.QTreeWidgetItem(rootItem)
                        catItem.setText(0, category)
                        if root == '2D':
                            continue
                        else:
                            for plot in sorted(CurveDict[root][category].keys()):
                                if plot not in notToShow:
                                    plotItem = QtWidgets.QTreeWidgetItem(catItem)
                                    plotItem.setText(0, plot)
                rootItem.setExpanded(True)
            
            self.saveSCAPSGenerationEnable()
                
            #self.CurveTreeWidget.expandAll()
            #self.CurveTreeWidget.sortItems(0,  QtCore.Qt.AscendingOrder)
    
        
    def showResultDetails(self):
        row = self.ResultTableView.selectionModel().selectedRows()[0].row()
        result = self.resultlist[row].scalars
        DetailDlg = ResultDetailDlg(result)
        DetailDlg.exec_()
        
        
    @pyqtSlot()
    def on_ConfigTableView_clicked(self):
        """
        open dialog to select which result values should be shown in ResultTableView
        dailog takes list of all available scalar values and 
        list of values to show
        """
        if self.resultlist:
            dialog = ConfigTableViewWidget(self.resultlist[0].scalars.keys(), self.defaults['scalars'])
            if dialog.exec_():
                self.defaults['scalars'] = dialog.setVisibleValues()
                self.resultmodel.beginResetModel()
                self.resultmodel.LabelList = self.defaults['scalars']
                self.resultmodel.endResetModel()
    
    @pyqtSlot()
    def on_deleteResult_clicked(self):
        """
        delete selected results from resultlist and stacklist of view model
        """
        if len(self.resultlist) > 0:
            if len(self.selectedRows) > 0:
                element = []
                self.resultmodel.beginResetModel()
                for i in self.selectedRows:
                    element.append(i)
                for offset, index in enumerate(element):
                    index -= offset
                    del self.resultlist[index]
                    del self.resultmodel.stacks[index]
                self.resultmodel.endResetModel()
                self.ResultTableView.selectRow(len(self.resultlist)-1)
        if len(self.resultlist) == 0:
            self.CurveTreeWidget.clear()
            
          
    @pyqtSlot()
    def on_reopenStack_clicked(self):
        selected = self.ResultTableView.selectionModel().selectedRows()
        if len(selected) == 1:
            result = self.resultlist[selected[0].row()]
            #print(selected[0].row())
            self.stack  = result.layerstack.stack
            self.StackNameEdit.setText(result.stackname)
            self.createStackView(1)
        elif len(selected) == 0:
            self.updateStatus('There is no result selected!') 
        else:
            self.updateStatus('There is more than one result selected!')
            
    
    @pyqtSlot()
    def on_plotCurve_clicked(self):
        """
        TODO: Slot documentation goes here.
        """
        toPlot = {}
        yLabel = ''
        yLabelCounter = 0
        selectedCurves = self.CurveTreeWidget.selectedItems()
        if selectedCurves:
            for item in selectedCurves:
                if item.childCount() == 0:
                    # collect all results for 2D plot
                    if item.text(0) == '2D':
                        return
                    if item.text(0) == 'profiles':
                        return
                    if item.parent().text(0) == '2D':
                        
                        for i, result in enumerate(self.selectedRows):
                            stack = self.resultlist[result]
                            if i == 0:
                                x = stack.x
                            if not set(stack.x) ==  set(x):
                                
                                continue
                            key = item.text(0)
                            toPlot[key + ' ( ' + stack.stackname + ')'] = [stack.x, stack.availablePlots['2D'][key].T]
                        self.plot_2D(toPlot, key)
                        return
                    for result in self.selectedRows:
                        stack = self.resultlist[result]
                        key = item.text(0)
                        toPlot[item.parent().text(0) + ' - ' + key + ' (' + stack.stackname + ')'] = stack.availablePlots \
                                    [item.parent().parent().text(0)] \
                                    [item.parent().text(0)] \
                                    [key]
                    if item.parent().parent().text(0) == 'spectra':
                        xRange = self.settings['wavelength']
                        xLabel = 'wavelength (nm)'
                    elif item.parent().parent().text(0) == 'profiles':
                        xRange = self.resultlist[result].x
                        xLabel = 'depth (nm)'
                    if item.parent().text(0) not in yLabel:
                        yLabelCounter += 1
                        if yLabelCounter > 1:
                            yLabel = yLabel + ', '
                        yLabel = yLabel + item.parent().text(0) 
                        
                elif item.childCount() > 0 and item.parent():
                    for result in self.selectedRows:
                        stack = self.resultlist[result]
                        for i in range(item.childCount()):
                            key = item.child(i).text(0)
                            toPlot[item.text(0) + ' - ' + key + ' (' + stack.stackname + ')'] = stack.availablePlots \
                                    [item.parent().text(0)] \
                                    [item.text(0)] \
                                    [key]
                            if item.parent().text(0) == 'spectra':
                                xRange = self.settings['wavelength']
                                xLabel = 'wavelength (nm)'
                            elif item.parent().text(0) == 'profiles':
                                xRange = self.resultlist[result].x
                                xLabel = 'depth (nm)'
                    if item.text(0) not in yLabel:
                        yLabelCounter += 1
                        if yLabelCounter > 1:
                            yLabel = yLabel + ', '
                        yLabel = yLabel + item.text(0)
                        
                elif not item.parent():
                    return
            PlotSubw = Subwindow((yLabel), xRange, toPlot, xLabel, yLabel)
            self.mdiArea.addSubWindow(PlotSubw)
            PlotSubw.show()
        
                    
            #elif not item.parent().parent()
                #curveName = item.
    def plot_2D(self, toPlot, key):
        if 'intensity' in key:
            ylabel = 'norm. intensity'
        else:
            ylabel = 'gen. rate (1/cm³s nm)'
        wvl = self.settings['wavelength']
        step = self.settings['wavelengthRange'][2]
        #dsf
        plot = ESubwindow(wvl, step, toPlot, ylabel)
        self.mdiArea.addSubWindow(plot)
        plot.show()
    
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QtWidgets.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/{}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action


    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
    
    def closeEvent(self, event):
        if self.okToContinue():
            self.AppSettings.setValue("LastFile", self.lastFile)
            self.AppSettings.setValue("RecentFiles", self.recentFiles or [])
            for filename in glob.glob("./tmp_*"):
                os.remove(filename) 
            #settings.setValue("MainWindow/Geometry", self.saveGeometry())
            #settings.setValue("MainWindow/State", self.saveState())
        else:
            event.ignore()

    def addRecentFile(self, fname):
        if fname is None:
            return
        if fname not in self.recentFiles:
            self.recentFiles = [fname] + self.recentFiles[:8]

    def okToContinue(self):
        if self.dirty:
            reply = QtWidgets.QMessageBox.question(self,
                    "OptiSim - Unsaved Changes",
                    "Save unsaved changes?",
                    QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No|QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Cancel:
                return False
            elif reply == QtWidgets.QMessageBox.Yes:
                return self.saveStack()
        return True
    
    def loadInitialFile(self):
        if self.lastFile is not "":
            if QtCore.QFile.exists(self.lastFile):
                try:
                    self.loadStack(self.lastFile)
                except LoadError as e:
                    self.warning(e.msg)
                    self.createDefaultStack()
                    self.fillSimulationOptions()
                    self.loadMaterialDB()
                
            else:
                self.updateStatus("could not open last file: {}".format(self.lastFile))
                self.createDefaultStack()
                self.fillSimulationOptions()
                self.loadMaterialDB()
        else:
            self.createDefaultStack()
            self.fillSimulationOptions()
            self.loadMaterialDB()

            
    def createDefaultStack(self):
        # create default stack
        #layer0 = Layer('Glass', 1000, 'constant', criConstant = [1.5, 0.0])
        #layer0.thick = True
		#self.stack = [layer0]
        #TODO: make sure these are in MateriaDB folder
        layer0 = Layer('ZnO', 800, 'from database', criDBName = 'nZnO_Richter_V1')
        layer1 = Layer('InS', 45, 'from database', criDBName = 'CdS_Richter')
        layer2 = Layer('CIS', 1600, 'from database', criDBName = 'CIS_Richter')
        layer3 = Layer('Mo', 200, 'from database', criDBName = 'Mo_Richter')
        self.stack = [layer0, layer1, layer2, layer3]
        
    def showReferences(self):
        references = ReferencesDlg(self.references, self)
        if references.exec_():
            self.references = references.references

    def showConfig(self):
        settings = ConfigDlg(self.settings, self.loadMaterialDB, self.lastFile, self)
        if settings.exec_():
            self.settings = settings.settings
            if settings.loadLastFile:
               self.lastFile = self.fileName
            else:
                self.lastFile = ""
            
    def updateStatus(self, message):
        self.statusBar().showMessage(message, 5000)
        if self.fileName:
            self.setWindowTitle("OptiSim ({}) - {}[*]".format(__version__,
                                os.path.basename(self.fileName)))
#        elif not self.image.isNull():
#            self.setWindowTitle("OptiSim - Unnamed[*]")
        else:
            self.setWindowTitle("OptiSim ({})[*]".format(__version__))
        self.setWindowModified(self.dirty)

    def onProgress(self, i):
        self.progressBar.setValue(i)

    def updateFileMenu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:-1])
        current = self.fileName
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QtCore.QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QtWidgets.QAction(QtGui.QIcon(":/icon.png"),
                        "&{} {}".format(i + 1, QtCore.QFileInfo(
                        fname).fileName()), self)
                action.setData(fname)
                action.triggered.connect(self.loadStack)
                self.fileMenu.addAction(action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.fileMenuActions[-1])
    
    def helpAbout(self):
        about, versions = strings.about(__version__)
        QtWidgets.QMessageBox.about(self, "About OptiSim",
                '{}\n{}'.format(about, versions))


    def helpHelp(self):
        #pass
        form = helpform.HelpForm("index.html", self)
        form.show()
    
    
    def warning(self, message):
        QtWidgets.QMessageBox.warning(self,
                    "Warning",
                    message,
                    QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Close))
    
    
    def startLogging(self):
        logging.basicConfig(format='', filename='LogFile.log', filemode='w', level=logging.INFO) #format='%(asctime)s %(message)s'
        logging.info(strings.startLog(__version__))
        logging.info('\nStart simulating structure on {} ...'.format(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())))
        # log all settings
        logging.info('\nsimulation settings:')
        for setting, value in self.settings.items():
            if setting == 'wavelength':
                continue
            if isinstance(value, list):
                output = ', '.join(map(str, value))
            else:
                output = str(value)
            logging.info('\t{}: {}'.format(setting, output))
       
    def stopLogging(self):
        logging.shutdown()
        
    
    
    
    @pyqtSlot()
    def  on_TMMexamplePB_clicked(self):
        pass
        #raise Exception("wow")
#        
#        x, y1, y2 = tmm.examples.sample1()
#        subw = Subwindow('tmm exmaple 1', x, {'Rnorm': y1, 'R45': y2}, 'wavenumeber (1/cm', 'Rnorm')
#        self.mdiArea.addSubWindow(subw)
#        subw.show()
    
    @pyqtSlot()
    def on_colorButton_clicked(self):
        color = QtWidgets.QColorDialog.getColor(self.currentLayer.color, self)
        if color.isValid():
            self.currentLayer.color = color
            self.dirty = True
            self.colorButton.setStyleSheet('background: %s' % color.name())
            self.createStackView(self.selectedLayer)
            #self.ButtonGroup.checkedButton.setStyleSheet('background: %s' % color.name())
    

    @pyqtSlot(bool)
    def on_calcStackOpticsCB_toggled(self, checked):
        if not checked:
            self.plotStackOpticsCB.setChecked(checked)
            self.calcFieldIntensityCB.setChecked(checked)
        self.updateDefaults()
    
    @pyqtSlot(bool)
    def on_calcFieldIntensityCB_toggled(self, checked):
        if not checked:
            self.plotFieldIntensityCB.setChecked(checked)
            self.calcLayerwiseOpticsCB.setChecked(checked)
            self.calcQECB.setChecked(checked)
        self.updateDefaults()
        
    @pyqtSlot(bool)
    def on_calcLayerwiseOpticsCB_toggled(self, checked):
        if not checked:
            self.plotLayerwiseOpticsCB.setChecked(checked)
            self.calcGenerationCB.setChecked(checked)
        self.updateDefaults()
        
    @pyqtSlot(bool)
    def on_calcQECB_toggled(self, checked):
        if not checked:
            self.plotQECB.setChecked(checked)
        self.updateDefaults()
        
    @pyqtSlot(bool)
    def on_calcGenerationCB_toggled(self, checked):
        if not checked:
            self.plotGenerationCB.setChecked(checked)
        self.updateDefaults()
        
    @pyqtSlot(bool)
    def on_calcEllipsometryCB_toggled(self, checked):
        if not checked:
            self.plotEllipsometryCB.setChecked(checked)
        self.updateDefaults()
        
    @pyqtSlot(bool)
    def on_calcOptBeamCB_toggled(self, checked):
        if not checked:
            self.plotOptBeamCB.setChecked(checked)
        self.updateDefaults()
        
    @pyqtSlot(bool)
    def on_plotStackOpticsCB_toggled(self, checked):
        self.updateDefaults()
    
    @pyqtSlot(bool)
    def on_plotFieldIntensityCB_toggled(self, checked):
        self.updateDefaults()
    
    @pyqtSlot(bool)
    def on_plotLayerwiseOpticsCB_toggled(self, checked):
        self.updateDefaults()
    
    @pyqtSlot(bool)
    def on_plotQECB_toggled(self, checked):
        self.updateDefaults()
    
    @pyqtSlot(bool)
    def on_plotGenerationCB_toggled(self, checked):
        self.updateDefaults()
    
    @pyqtSlot(bool)
    def on_plotEllipsometryCB_toggled(self, checked):
        self.updateDefaults()
    
    @pyqtSlot(bool)
    def on_plotOptBeamCB_toggled(self, checked):
        self.updateDefaults()
        
    def updateDefaults(self):
        self.defaults['calculations'] = []
        self.defaults['plots'] = []
        for i, CB in enumerate(self.calcOptionsCB):
            if CB.isChecked():
                self.defaults['calculations'].append(i)
        for i, CB in enumerate(self.plotOptionsCB):
            if CB.isChecked():
                self.defaults['plots'].append(i)
        self.updateStatus('')
        self.dirty = True
    
    @pyqtSlot(int)
    def on_SCRwidthSB_valueChanged(self, p0):
        if not self.currentLayer.collection['SCRwidth'] == p0:
            self.currentLayer.collection['SCRwidth'] = p0
            self.currentLayer.makeXcollection()
            self.plotCollectionFunction()
            self.dirty = True
    
    @pyqtSlot(int)
    def on_diffLengthSB_valueChanged(self, p0):
        if not self.currentLayer.collection['diffLength'] == p0:
            self.currentLayer.collection['diffLength'] = p0
            self.currentLayer.makeXcollection()
            self.plotCollectionFunction()
            self.dirty = True
            
    @pyqtSlot(float)
    def on_recVelLE_valueChanged(self, p0):
        if not self.currentLayer.collection['recVel'] == p0:
            self.currentLayer.collection['recVel'] = p0
            self.currentLayer.makeXcollection()
            self.plotCollectionFunction()
            self.dirty = True
            
    @pyqtSlot(float)
    def on_collectionGradingSB_valueChanged(self, p0):
        if not self.currentLayer.collection['grading'] == p0:
            self.currentLayer.collection['grading'] = p0
            self.currentLayer.makeXcollection()
            self.plotCollectionFunction()
            self.dirty = True

    @pyqtSlot(bool)
    def on_SCRbottom_toggled(self, checked):
        # top = 0, bottom = 1
        if not self.currentLayer.collection['SCRside'] == checked:
            self.currentLayer.collection['SCRside'] = checked
            self.currentLayer.makeXcollection()
            self.plotCollectionFunction()
            self.dirty = True
    
    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            #selected = self.ResultTableView.selectedRanges()    

            if e.key() == QtCore.Qt.Key_C: #copy
#                s = ""
#
#                for r in range(selected[0].topRow(), selected[0].bottomRow()+1):
#                    for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
#                        try:
#                            s += str(self.ResultTableView.item(r,c).text()) + "\t"
#                        except AttributeError:
#                            s += "\t"
#                    s = s[:-1] + "\n" #eliminate last '\t'
#                self.clip.setText(s)
#                
                '''
                Copy the table selection to the clipboard
                '''
                selection = self.ResultTableView.selectionModel()
                indexes = selection.selectedIndexes()
                indexes.sort()
                previous = indexes.pop(0)
                data = self.ResultTableView.model().data(previous)
                text = data
                selected_text = text
          
                for current in indexes:
                    if current.row() != previous.row():
                        selected_text += '\n'
                    else:
                        selected_text += '\t'
                    data = self.ResultTableView.model().data(current)
                    text = data
                    selected_text += text
                    previous = current
                selected_text += '\n'
                QtWidgets.QApplication.clipboard().setText(selected_text)
    
    @pyqtSlot()
    def on_defineDielectricFunc_clicked(self):
        dielFunc = dielectricFunctionDlg(self.currentLayer, self)
        if dielFunc.exec_():
            self.currentLayer.dielectricFunction = dielFunc.dielectricFunction
            self.plotDielectricFunction()
            
            self.dirty = True
            self.updateStatus("Model for dielectric function for {} updated".format(self.currentLayer.name))
    
    def plotDielectricFunction(self):
        #TODO: perform this after change layer selection
        n = self.currentLayer.dielectricFunction['n']
        k = self.currentLayer.dielectricFunction['k']
        wvl = self.currentLayer.dielectricFunction['wvl']
        self.dielectricPlot.canvas.ax.clear() 
        self.dielectricPlot.canvas.ax.set_xlabel('wavelength (nm)')
        self.dielectricPlot.canvas.ax.set_ylabel('n, k')
        if not n == []:
            self.dielectricPlot.canvas.ax.plot(wvl, n, wvl, k)
        self.dielectricPlot.canvas.draw()
    
    @pyqtSlot()
    def on_extractBandgapPB_clicked(self):
        self.getCRI(self.currentLayer)
        ExtractBandgap = ExtractBandgapDlg(self.currentLayer.wavelength, self.currentLayer.k, self)
        
        if ExtractBandgap.exec_():
            pass
    

