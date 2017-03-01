# -*- coding: utf-8 -*-

"""
Module implementing dielectricFunctionDlg.
"""

from PyQt5.QtCore import pyqtSlot, QItemSelectionModel, Qt
from PyQt5.QtWidgets import QDialog, QLabel, QDoubleSpinBox, QFileDialog

from .Ui_dielectric_function import Ui_Dialog

import numpy as np
import numexpr as ne
from scipy import integrate

from classes.errors import *
from classes.navtoolbar import NavToolBar, DraggableLegend

MODELS = { 'Gaussian' : {  'parameter': ['Amp', 'En', 'Br'], 
                                        'defaults': [1, 3, 0.2], 
                                        'function': 'Amp*exp(-((eV-En)/(Br/(2*sqrt(log(2)))))**2) - Amp*exp(-((eV+En)/(Br/(2*sqrt(log(2)))))**2)'}, 
                        'Drude' :  {  'parameter': ['Amp', 'Br'], 
                                        'defaults': [1, 0.2], 
                                        'function': '(Amp*Br)/(eV**2+complex(0, Br*eV))'},
                        'Lorentz' :  {  'parameter': ['Amp', 'En', 'Br'], 
                                        'defaults': [1, 3, 0.2], 
                                        'function': '(Amp*Br*En)/(En**2-eV**2-complex(0, Br*eV))'},  
                        'Tauc-Lorentz' :  {  'parameter': ['Amp', 'En', 'C', 'Eg'], 
                                        'defaults': [20, 4, 0.5, 3.5], 
                                        'function': '(Amp*C*En*(eV-Eg)**2)/(eV*((eV**2-En**2)**2+C**2*eV**2))'}, 
                        'Cody-Lorentz' :  {  'parameter': ['Amp', 'En', 'Br', 'Eg', 'Ep', 'Et', 'Eu'], 
                                        'defaults': [20, 4, 0.1, 2.5, 1, 0, 0.5], 
                                        'function': ['(((eV-Eg)**2)/((eV-Eg)**2+Ep**2)) * (Amp*En*Br*eV)/((eV**2-En**2)**2+Br**2*eV**2)', 
                                                    '(Et*(((eV-Eg)**2)/((eV-Eg)**2+Ep**2)) * (Amp*En*Br*eV)/((eV**2-En**2)**2+Br**2*eV**2)/eV)*exp((eV-Eg-Et)/Eu)'
                                                    ]}
                                        }

def calcFunction(dielectricFunction):
    models = MODELS
    oscillators = dielectricFunction['oscillators']
    eV = np.linspace(  dielectricFunction['spectral range'][0],
                            dielectricFunction['spectral range'][1], 
                            100)

    dielectricFunction['wvl'] = 1239.941 / eV
    
    e_offset = dielectricFunction['e0']
    e = e_offset
    for osci in oscillators:
        if osci['active']:
            name = osci['name']
            for i, value in enumerate(osci['values']):
                string = '{} = {}'.format(models[name]['parameter'][i], value)
                exec(string)
            if name in ['Drude', 'Lorentz']:
                e_osci = ne.evaluate(models[name]['function'])
            else:
                if name == 'Tauc-Lorentz': # 0 for E > Eg, function for <= Eg
                    e2_osci = np.zeros(len(eV))
                    e2_func = ne.evaluate(models[name]['function'])
                    e2_osci[eV > osci['values'][3]] = e2_func[eV > osci['values'][3]]
                elif name == 'Cody-Lorentz': # function 1 for E > (Eg+Et), function2 for 0<E<=(Eg+Et)
                    e2_osci = np.zeros(len(eV))
                    e2_func1 = ne.evaluate(models[name]['function'][0])
                    e2_func2 = ne.evaluate(models[name]['function'][1])
                    e2_osci[eV > osci['values'][3] + osci['values'][5]] = e2_func1[eV > osci['values'][3] + osci['values'][5]]
                    e2_osci[eV <= osci['values'][3] + osci['values'][5]] = e2_func2[eV <= osci['values'][3] + osci['values'][5]]
                    
                else: # e.g. Gaussian
                    e2_osci = ne.evaluate(models[name]['function'])
                    
                e1_osci = KKR(e2_osci, eV)
                e_osci = e1_osci + 1j * e2_osci
                
            e = e + e_osci
            e1 = np.real(e)
            e2 = np.imag(e)
            
            dielectricFunction['n'] = (0.5 * (e1 + (e1**2 + e2**2)**0.5))**0.5
            dielectricFunction['k'] = (0.5 * (-e1 + (e1**2 + e2**2)**0.5))**0.5
    return e1,  e2, dielectricFunction, eV

def KKR(e2, eV):
    '''
    KKR e1(E) = 2/pi P integral_0ûnendl(E'e2(E) dE'/(E'^2-E^2)) + 1
    
    '''
    
    E = eV
    e1 = np.zeros(len(eV))
    
    # first element is computed without integrating the first energy value
    e1[0] = 1 + (2 / np.pi) * integrate.trapz(E[1:-1] * e2[1:-1] / (E[1:-1]**2 - E[0])) * (E[3]-E[2])
    
    #e1[-1] = 1 + (2 / np.pi) * integrate.trapz(E[0:-2] * e2[0:-2] / (E[0:-2]**2 - E[-1]))
    
    
    for i in range(1, len(E)):
        e1_part1 = integrate.trapz(E[0:i-1] * e2[0:i-1] / (E[0:i-1]**2 - E[i]**2))
        e1_part2 = integrate.trapz(E[i+1:-1] * e2[i+1:-1] / (E[i+1:-1]**2 - E[i]**2))
        
        e1[i] = 1 + (2 / np.pi) * (e1_part1 + e1_part2) * (E[3]-E[2])
        
    return e1

def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            raise LoadError('Can not convert string {} into number!'.format(s))




class dielectricFunctionDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, layer, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super(dielectricFunctionDlg, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() |
                              Qt.WindowSystemMenuHint |
                              Qt.WindowMinMaxButtonsHint)
                              
        self.dielectricFunction = layer.dielectricFunction.copy()
        self.oscillators = self.dielectricFunction['oscillators']
        
        self.possibleOscillators = ['Gaussian', 'Drude', 'Lorentz', 'Tauc-Lorentz', 'Cody-Lorentz']
        self.oscillatorComboB.addItems(self.possibleOscillators)
        
        self.models = MODELS
        
        self.currentSelection = 0
        self.referenceFlag = False
        self.fillWidgets()
        
        
    def fillWidgets(self):
        self.e0SB.setValue(self.dielectricFunction['e0'])
        self.starteVSB.setValue(self.dielectricFunction['spectral range'][0])
        self.endeVSB.setValue(self.dielectricFunction['spectral range'][1])
        self.update_listOscillator()
        
    @pyqtSlot(float)
    def on_e0SB_valueChanged(self, p0):
        self.dielectricFunction['e0'] = p0
        self.plotFunction()
    
    @pyqtSlot()
    def on_addOscillator_clicked(self):
        osciName = self.oscillatorComboB.currentText()        
        self.oscillators.append({'name': osciName, 'values': self.models[osciName]['defaults'].copy(), 'active': True})
        #print(self.oscillators)
        self.currentSelection = len(self.oscillators) - 1
        self.update_listOscillator()

    @pyqtSlot()
    def on_removeOscillator_clicked(self):
        idx = self.listOscillator.currentRow()
        self.oscillators.pop(idx)
        self.currentSelection = len(self.oscillators)-2
        self.update_listOscillator()
    
    @pyqtSlot(int)
    def on_listOscillator_currentRowChanged(self, currentRow):
        for i in reversed(range(self.detailsLayout.count())):
            self.detailsLayout.itemAt(i).widget().deleteLater()
        
        index = self.listOscillator.currentRow()
        if index > -1:
            self.osci = self.oscillators[index]
            name =self.osci['name']
            label = QLabel(name)
            self.detailsLayout.addWidget(label)
            for i, value in enumerate(self.osci['values']):
                label = QLabel(self.models[name]['parameter'][i])
                SB = QDoubleSpinBox()
                SB.setRange(0.00, 9999.9)
                SB.setDecimals(4)
                SB.setSingleStep(0.1)
                SB.setValue(value)
                SB.editingFinished.connect(self.valuesChanged)
                self.detailsLayout.addWidget(label)
                self.detailsLayout.addWidget(SB)
  
            self.activeOscillatorCB.setChecked(self.osci['active'])
            self.currentSelection = currentRow
        
    @pyqtSlot()
    def valuesChanged(self):
        j = 0
        for i in range(self.detailsLayout.count()):
            if i > 1 and i%2 == 0:
                widget = self.detailsLayout.itemAt(i).widget()
                #if widget.hasFocus():
                 #   pass
                #else:
                try:
                    value = widget.value()
                    self.oscillators[self.currentSelection]['values'][j] = widget.value()
                except:
                    pass
                
                j += 1
        self.update_listOscillator() 
        
    #@pyqtSlot(bool)
    #def on_activeOscillatorCB_toggled(self, checked):
            
    @pyqtSlot(bool)
    def on_activeOscillatorCB_clicked(self, checked):
        self.osci['active'] = checked
        self.update_listOscillator()
        
    def update_listOscillator(self):
        #clean first
        self.listOscillator.clear()
        #for SelectedItem in self.listOscillator.selectedItems():
        #    self.listOscillator.takeItem(self.listOscillator.ContentList.row(SelectedItem))
        #    
        for idx, item in enumerate(self.oscillators):
            values = ', '.join(map(str,item['values']))
            if item['active']:
                active = ''
            else:
                active = '~'
    
            string = '{}{} {} (values: {})'.format(active, idx, item['name'], values)
            self.listOscillator.addItem(string)
        
        self.listOscillator.setCurrentRow(self.currentSelection, QItemSelectionModel.SelectCurrent)
        self.plotFunction()
        
    def plotFunction(self):
        self.calcFunction()
        if self.referenceFlag:
            e1ref = np.interp(self.eV, self.eVref, self.e1ref)
            e2ref = np.interp(self.eV, self.eVref, self.e2ref)
            curves = {'e1': self.e1, 'e2': self.e2, 'ref e1': e1ref, 'ref e2': e2ref}
        else:
            curves = {'e1': self.e1, 'e2': self.e2}
            
        self.dielectricFunctionPlot.showCurves(self.eV, curves, 'energy (eV)', 'e1 and e2')
        self.opticalConstantsPlot.showCurves(1239.94051/self.eV, {'n': self.dielectricFunction['n'] , 'k': self.dielectricFunction['k'] }, 'wavelength (nm)', 'optical constants')
        
    def calcFunction(self):
        self.e1, self.e2, self.dielectricFunction, self.eV = calcFunction(self.dielectricFunction)

    
    @pyqtSlot(float)
    def on_starteVSB_valueChanged(self, p0):
        eV = 1239.94051/p0
        self.starteVLabel.setText('{} nm'.format(eV))
        self.dielectricFunction['spectral range'][0] = p0  
        self.plotFunction()
    
    @pyqtSlot(float)
    def on_endeVSB_valueChanged(self, p0):
        eV = 1239.94051/p0
        self.endeVLabel.setText('{} nm'.format(eV))
        self.dielectricFunction['spectral range'][1] = p0
        self.plotFunction()
    
    @pyqtSlot()
    def on_loadReference_clicked(self):
        file, _ = QFileDialog.getOpenFileName()
        # if a file is selected
        if file:
            eV = []
            e1 = []
            e2 = []
            with open(file) as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line[0].isdigit():
                        fields = line.split("\t")
                        eV.append(num(fields[0]))
                        e1.append(num(fields[1]))
                        e2.append(num(fields[2]))

            f.close()
            self.referenceFlag = True
            if eV[2] < eV[1]:
                eV = eV[::-1]
                e1 = e1[::-1]
                e2 = e2[::-1]
            self.eVref = eV
            self.e1ref = e1
            self.e2ref = e2
            self.plotFunction()


