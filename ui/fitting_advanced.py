# -*- coding: utf-8 -*-

"""
Module implementing FittingAdvancedDlg.
"""

import time
import copy
import numpy as np
from scipy.optimize import minimize # minimize_scalar, basinhopping, curve_fit


from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QHeaderView, QMessageBox

from .Ui_fitting_advanced import Ui_Dialog
from .dielectric_function import MODELS
from .dielectric_function import calcFunction as calcOsciFunction


from classes.layerstack import LayerStack
from classes.optics import Optics
#from classes.advancedFitingTreeModel import TreeOfParamtersModel


class FittingAdvancedDlg(QDialog, Ui_Dialog):
    '''
    The tree should provide any fittable parameter of any layers
    layer 1                                                     value               *what to change*            
        - thickness                                                                 layer.thickness
        - srough_thickness (if model is on)                                  if layer.srough: layer.sroughThickness
        - haze reflection (if model is on)                                     if layer.srough: layer.sroughHazeR
        - haze transmission (if model is on)                                 if layer.srough: layer.sroughHazeT
        - constant n (if source is constant)                                if layer.criSource=='constant': layer.criConstant[0] 
        - constant k (if source is constant)                                if layer.criSource=='constant': layer.criConstant[1] 
        - grading (constant) (if source is constant)                     if layer.criSource=='graded' && layer.criGrading['mode']=='constant':  layer.criGrading['value']
        + dielectric function (if source)                                       if layer.criSource=='dielectric function'
            - e0                                                                        layer.dielectricFunction['e0']
            + oscillator 0                                                          for each oscillator: layer.dielectricFunction['oscillators'][#of Osci]['name'] : [{'name': 'Lorentz', 'values': [1, 3, 0.2], 'active': True}], 
                - value 1                                                           layer.dielectricFunction['oscillators'][#of Osci]['value'][0]
                - value 2 ...
            + oscillator 1
                - value 1 ..
        - collection function (constant) (if selected)                     if layer.collection['source'] == 'from collection function' && layer.collection['mode'] == 'constant': layer.collection['value']
        + diff length model                                                       if layer.collection['source'] == 'from diffusion length'
            - space charge region width                                      layer.collection['SCRwidth']
            - diff length                                                           layer.collection['diffLength']
            - surface rec. velocity                                             layer.collection['recVel']
    layer 2
        ...

    '''
    def __init__(self, stack, references, stackname, settings, getcri, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super().__init__(parent)
        self.setupUi(self)        
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.originalStack = stack
        self.stack = copy.deepcopy(stack)
        self.references = references
        self.StackName = stackname
        self.settings = settings
        self.getCRI = getcri
        
        self.referenceDataSelected = {}
        self.referenceList = []
        for key, value in self.references.items():
            if value[0]:
                self.referenceList.append([key, False]) # name and selection for fitting 
        self.referenceListModel = QStandardItemModel()
        self.referenceListModel.itemChanged.connect(self.updateReferences)
        self.referenceListView.setModel(self.referenceListModel)
        self.fillReferences()
        
        self.parameterModel = QStandardItemModel() #TreeOfParametersModel()
        self.parameterTreeView.setModel(self.parameterModel)
        self.parameterModel.setHorizontalHeaderLabels(['Parameter', 'Value'])
        self.root = self.parameterModel.invisibleRootItem()
        self.fillParameterTree()
        

        
        # configurations
        self.noOfFitIterations = 100
        methods = ['Nelder-Mead', 'Powell', 'CG', 'BFGS', 'L-BFGS-B', 'TNC', 'COBYLA', 'SLSQP']
        self.tolerance = 1e-3
         # with Jacobian necessary: 'Newton-CG', 'dogleg',  'trust-ncg'
        self.configuration = dict([
                        ('method', methods[0]),
                        ('noOfIterations', self.noOfFitIterations), 
                        ('tolerance', self.tolerance), 
                        ('plotInBetween',  True)
                        ])
        self.methodCB.addItems(methods)
        self.noOfIterationsSB.setValue(self.noOfFitIterations) 
        self.toleranceSB.setValue(self.tolerance)
        
        try:
            self.runOptics()
        except:
            self.done(0)
            QMessageBox.warning(self, "error", 'Error - could not calculate current stack.\nPlease check stack definition until simple simulation is running.',
                QMessageBox.StandardButtons(QMessageBox.Close))
            
            
    def fillReferences(self):
        
        for value in self.referenceList:                   
            item = QStandardItem(value[0])
            check = Qt.Checked if value[1] else Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            self.referenceListModel.appendRow(item)
    
    def updateReferences(self):
        self.referenceDataSelected = {}
        for row in range(self.referenceListModel.rowCount()):
            item = self.referenceListModel.item(row)                  
            if item.checkState() == Qt.Checked:
                self.referenceList[row][1] = True
                self.referenceDataSelected[item.text()] = self.referenceData[item.text()]
            else:
                self.referenceList[row][1] = False
        self.updatePlot()
        #print(len(self.referenceDataSelected))
            #print('{} {}'.format(row, self.references[row]))
        
    def updatePlot(self):
        plotDict = {}
        for ref in self.referenceList:
            if ref[1]:
                if ref[0] == 'R reference':
                    plotDict['R reference'] = self.referenceData['R reference']
                    plotDict['R'] = self.optics.RspectrumSystem
                if ref[0] == 'T reference':                    
                    plotDict['T reference'] = self.referenceData['T reference']
                    plotDict['T'] = self.optics.TspectrumSystem
                if ref[0] == 'EQE reference':
                    plotDict['EQE reference'] = self.referenceData['EQE reference']
                    plotDict['EQE'] = self.optics.EQE
                if ref[0] == 'psi reference':
                    plotDict['psi reference'] = self.referenceData['psi reference']
                    plotDict['psi'] = self.optics.psi
                if ref[0] == 'delta reference':
                    plotDict['delta reference'] = self.referenceData['delta reference']
                    plotDict['delta'] = self.optics.delta
        x = self.optics.wavelength
        if plotDict:
            self.plotView.showCurves(x, plotDict, 'wavelength (nm)', 'value [a.u.]')
        else:
            self.plotView.ax.clear()
            self.plotView.canvas.draw()
        
    def fillParameterTree(self):
        rows = self.parameterModel.rowCount()
        if rows:
            while self.parameterModel.rowCount() > 0:
                self.parameterModel.removeRow(0)
        self.parameterList = []
        parameterStr = 'self.stack['
        
        for i, layer in enumerate(self.stack):
            parameterStr += '{}].'.format(i)
            layerBranch = QStandardItem(layer.name)
            self.root.appendRow(layerBranch)
            self.addTreeEntry(layerBranch, 'thickness (nm)',  layer.thickness, self.changeThickness)
            if layer.srough:
                self.addTreeEntry(layerBranch, 'thickness roughness layer (nm)', layer.sroughThickness, self.changeSroughThickness)
                self.addTreeEntry(layerBranch, 'Haze R', layer.sroughHazeR, self.changeSroughHazeR)
                self.addTreeEntry(layerBranch, 'Haze T', layer.sroughHazeT, self.changeSroughHazeT)
            if layer.criSource=='constant':
                self.addTreeEntry(layerBranch, 'constant n', layer.criConstant[0], self.changeConstantn)
                self.addTreeEntry(layerBranch, 'constant k', layer.criConstant[1], self.changeConstantk)
            if layer.criSource=='graded' and layer.criGrading['mode']=='constant':
                self.addTreeEntry(layerBranch, 'constant grading', layer.criGrading['value'], self.changeConstantGrading)
            if layer.criSource=='dielectric function':
                criBranch = QStandardItem('dielectric function parameters')
                layerBranch.appendRow(criBranch)
                self.addTreeEntry(criBranch, 'e0', layer.dielectricFunction['e0'],  self.changeConstante, level = 2)
                for idx, oscillator in enumerate(layer.dielectricFunction['oscillators']):
                    osciBranch = QStandardItem('{} {}'.format(idx, oscillator['name']))
                    criBranch.appendRow(osciBranch)
                    parameterNames = MODELS[oscillator['name']]['parameter']
                    for i, value in enumerate(oscillator['values']):
                        self.addTreeEntry(osciBranch, parameterNames[i], value, self.changeOscillator, level = 3)
            if layer.collection['source'] == 'from collection function' and layer.collection['mode'] == 'constant':
                self.addTreeEntry(layerBranch, 'constant collection efficiency', layer.collection['value'], self.changeConstantCollection)
            if layer.collection['source'] == 'from diffusion length':
                collectionBranch = QStandardItem('collection model')
                layerBranch.appendRow(collectionBranch)
                self.addTreeEntry(collectionBranch, 'space charge region width (nm)', layer.collection['SCRwidth'],  self.changeSCR, level = 2)
                self.addTreeEntry(collectionBranch, 'diffusion length (nm)', layer.collection['diffLength'], self.changeDiffL, level = 2)
                self.addTreeEntry(collectionBranch, 'recombination velocity (cm/s)', layer.collection['recVel'], self.changerecVel, level = 2)
        
        self.parameterTreeView.setColumnWidth(1, 80)
        self.parameterTreeView.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.parameterTreeView.expandAll()

    def addTreeEntry(self, parent, name, parameter, func, level = 1):
        child = QStandardItem(name)
        child.setCheckable(True)
        value = QStandardItem(str(parameter))
        parent.appendRow([child, value])
        
        if level == 3:
            osciNum = parent.parent().rowCount() - 2
            itemNum = parent.rowCount() - 1
            self.parameterList.append([parameter, func, osciNum, itemNum])
        else:
            self.parameterList.append([parameter, func])
            
            
    def getSelectedValues(self):
        selected = [] # name, layer number, initial value, function to change
        i = 0
        for row in range(self.parameterModel.rowCount()):
            layer = self.parameterModel.item(row)
            for row1 in range(layer.rowCount()):
                child1 = layer.child(row1)
                if not child1.hasChildren():
                    if child1.checkState() == Qt.Checked:
                        selected.append([child1.text(), row, self.parameterList[i][0], self.parameterList[i][1]])
                    i += 1
                else:
                    for row2 in range(child1.rowCount()):
                        child2 = child1.child(row2)
                        if not child2.hasChildren():
                            if child2.checkState() == Qt.Checked:
                                selected.append([child2.text(), row, self.parameterList[i][0], self.parameterList[i][1]])
                            i += 1
                        else:
                            for row3 in range(child2.rowCount()):
                                child3 = child2.child(row3)
                                if child3.checkState() == Qt.Checked:
                                    selected.append([child3.text(), row, self.parameterList[i][0], self.parameterList[i][1], self.parameterList[i][2], self.parameterList[i][3]])
                                i += 1
        return selected
    
    @pyqtSlot()
    def on_testPB_clicked(self):
        selected = self.getSelectedValues()
        str = ''
        #print(selected)
        for item in selected:
            str += '{} {}\n'.format(item[0], item[1]) 
            self.resultTextEdit.setText(str)
        self.plot()
        if selected:
            layer = selected[0][1]
            func = selected[0][2]
            value = 250
            func(layer, value)
            #print(self.parameterList)
            #self.parameterList[0][0] = 300
            #print('stack {}'.format(self.stack[0].thickness))
            
            
    def runOptics(self):
        input = LayerStack(self.StackName, self.stack, self.settings, self.getCRI)
        self.optics = Optics(self.StackName, input, self.references, self.settings)
        self.optics.calcStack()
        self.optics.createReferenceCurves()
        self.optics.calcFieldIntensity()
        self.optics.calcAbsorption()
        self.optics.calcQE()
        self.optics.calcEllipsometry()
        #get reference data
        self.referenceData = {}
        
        for ref in self.referenceList:
            if ref[0] == 'R reference':
                self.referenceData['R reference'] = self.optics.R_reference
            elif ref[0] == 'T reference':
                self.referenceData['T reference'] = self.optics.T_reference
            elif ref[0] == 'EQE reference':
                 self.referenceData['EQE reference'] = self.optics.EQE_reference
            elif ref[0] == 'psi reference':
                self.referenceData['psi reference'] = self.optics.psi_reference
            elif ref[0] == 'delta reference':
                self.referenceData['delta reference'] = self.optics.delta_reference

        
    @pyqtSlot()
    def on_startFittingPB_clicked(self):
        if not self.referenceDataSelected:
            QMessageBox.warning(self, "error", 'Error - no reference curve selected!\n',
                QMessageBox.StandardButtons(QMessageBox.Close))
            return
            
        parameterList = self.getSelectedValues()
        if not parameterList:
            QMessageBox.warning(self, "error", 'Error - no fitting parameter selected!\n',
                QMessageBox.StandardButtons(QMessageBox.Close))
            return
        self.resultTextEdit.setPlainText("")
               
        start_time = time.time()

        #get initial deviation
            
        #get initial values
        parameters = []
        for item in parameterList:
            parameters.append(item[2])
        # run fitting
        try:
            self.resultTextEdit.setText("busy fitting ...")
            minResult = minimize(self.minimizeFunction, parameters, args = (parameterList),
                                    method= self.configuration['method'], tol=self.configuration['tolerance'], 
                                    options = {'maxiter' : self.configuration['noOfIterations']}) #, tol=1e-6
        except RuntimeError as e:
            QMessageBox.warning(self, "fitting error", 'Error - curve fitting failed!\n{}'.format(e.args[0]),
                QMessageBox.StandardButtons(QMessageBox.Close))
            return
        
        # run all optics to get other curves when references are changed
        self.runOptics()
        # to make sure at least the last result is plotted
        self.updatePlot()
        
        duration = time.time() - start_time
        message = "The optimized parameters are:\n"
        for i, item in enumerate(parameterList):
            message += "{} of {} --> {}\n".format(item[0], self.stack[item[1]].name, minResult.x[i])
        message += "Details: {}\nNumber of Iterations: {}\nNumber of function calls: {}\nChi-square: {:7.4f}\nFitting time: {:7.2f} seconds".format(
                            minResult.message, minResult.nit, minResult.nfev, minResult.fun, duration)
        self.resultTextEdit.setText(message)
        self.fillParameterTree()
        #logging.info('\n' + 50 * '#' + '\n' + message + '\n do final calculation ...\n' + 50 * '#')

    def minimizeFunction(self, values, parameterList):
        #set the parameters
        for i, value in enumerate(values):
            layer = parameterList[i][1]
            func = parameterList[i][3]
            if func == self.changeOscillator:
                osciNum = parameterList[i][4]
                itemNum = parameterList[i][5]
                func(layer, osciNum, itemNum, value)
            else:
                func(layer, value)
        input = LayerStack(self.StackName, self.stack, self.settings, self.getCRI)
        self.optics = Optics(self.StackName, input, self.references, self.settings)
        self.optics.calcStack()
        #print(len(self.referenceDataSelected))
        errorArray = np.zeros(len(self.optics.wavelength))
        for key, exp in self.referenceDataSelected.items():
            if key == 'R reference':
                model = self.optics.RspectrumSystem
                errorArray += ((model - exp)/exp)**2
            elif key == 'T reference':
                model = self.optics.TspectrumSystem
                errorArray += ((model - exp)/exp)**2
            elif key == 'EQE reference':
                self.optics.calcFieldIntensity()
                self.optics.calcAbsorption()
                self.optics.calcQE()
                model = self.optics.EQE
                errorArray += ((model - exp)/exp)**2
            elif key == 'psi reference':
                self.optics.calcEllipsometry()
                model = self.optics.psi
                errorArray += ((model - exp)/exp)**2
            elif key == 'delta reference':
                self.optics.calcEllipsometry()
                model = self.optics.delta
                errorArray += ((model - exp)/exp)**2
        #N = len(errorArray)
        #M = len(parameterList)
        if self.configuration['plotInBetween']:
            self.updatePlot()
        return np.sum(errorArray) # chi² or MSE = 1/(2N-M) * chi² 
        
    @pyqtSlot(str)
    def on_methodCB_currentIndexChanged(self, p0):
       self.configuration['method'] = p0
       
    @pyqtSlot(int)
    def on_noOfIterationsSB_valueChanged(self, p0):
        self.configuration['noOfIterations'] = p0

    def changeThickness(self, layer, value):
        self.stack[layer].thickness = int(value)
        
    def changeSroughThickness(self, layer, value):
        self.stack[layer].sroughThickness = int(value)
        
    def changeSroughHazeR(self, layer, value):
        self.stack[layer].sroughHazeR = value
        
    def changeSroughHazeT(self, layer, value):
        self.stack[layer].sroughHazeT = value
        
    def changeConstantn(self, layer, value):
        self.stack[layer].criConstant[0] = value
        
    def changeConstantk(self, layer, value):
        self.stack[layer].criConstant[1] = value
        
    def changeConstantGrading(self, layer, value):
         self.stack[layer].criGrading['value'] = value
         
    def changeConstante(self, layer, value):
        self.stack[layer].dielectricFunction['e0'] = value
        e1, e2, self.stack[layer].dielectricFunction, eV = calcOsciFunction(self.stack[layer].dielectricFunction)
        
    def changeConstantCollection(self, layer, value):
         self.stack[layer].collection['value'] = value
         self.stack[layer].makeXcollection()
         
    def changeSCR(self, layer, value):
        self.stack[layer].collection['SCRwidth'] = int(value)
        self.stack[layer].makeXcollection()
        
    def changeDiffL(self, layer, value):
        self.stack[layer].collection['diffLength'] = int(value)
        self.stack[layer].makeXcollection()
        
    def changerecVel(self, layer, value):
        self.stack[layer].collection['recVel'] = value
        self.stack[layer].makeXcollection()
        
    def changeOscillator(self, layer, osciNum, itemNum, value):
        self.stack[layer].dielectricFunction['oscillators'][osciNum]['values'][itemNum] = value
        e1, e2, self.stack[layer].dielectricFunction, eV = calcOsciFunction(self.stack[layer].dielectricFunction)
    
    @pyqtSlot()
    def on_reloadPB_clicked(self):
        self.stack = self.originalStack
        self.fillParameterTree()
    
    @pyqtSlot(float)
    def on_toleranceSB_valueChanged(self, p0):
        self.configuration['tolerance'] = p0
    
    @pyqtSlot(bool)
    def on_plotInBetweenCB_toggled(self, checked):
        self.configuration['plotInBetween'] = checked
