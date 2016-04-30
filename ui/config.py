# -*- coding: utf-8 -*-

"""
Module implementing ConfigDlg.
"""

import os
import numpy as np
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog, QFileDialog

from .Ui_config import Ui_Dialog


class ConfigDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, settings, loadMaterialDB, lastFile, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.reloadMaterialDB = loadMaterialDB
        self.settings = settings.copy()
        
        if 'roughness Haze calc diffuse' not in self.settings:
            self.settings['roughness Haze calc diffuse'] = [True, 20, 0.00001]
            
            
        if lastFile is not "":
            self.loadLastFile = True
        else:
            self.loadLastFile = False
        
        self.fillWidgets()

    def fillWidgets(self):
        # excitation
        self.intensitySlider.setValue(self.settings['intensity'])
        self.fillSpectra()
        #self.intensityLabel.setText('{}%'.format(self.settings['intensity']))
        self.angleSB.setValue(self.settings['angle'])
        
        # spectrum(self.settings['wavelengthRange'][0])
        self.startSB.setValue(self.settings['wavelengthRange'][0])
        self.endSB.setValue(self.settings['wavelengthRange'][1])
        self.stepSB.setValue(self.settings['wavelengthRange'][2])

        # calculation options
        self.LBcorrectForReflCB.setChecked(self.settings['LB correct for Reflection'])
        self.gradingAdvancedCB.setChecked(self.settings['grading advanced'])
        self.roughEMACB.setChecked(self.settings['roughness EMA model'])
        self.roughFresnelCB.setChecked(self.settings['roughness Fresnel model'])
        self.calcDiffuseLightCB.setChecked(self.settings['roughness Haze calc diffuse'][0])
        
        self.RaytracerIterationsSB.setValue(self.settings['roughness Haze calc diffuse'][1])
        self.RaytracerIntensitySB.setValue(self.settings['roughness Haze calc diffuse'][2])
        
        # EMA models
        if 'EMA model' in self.settings:
            EMAmodel = self.settings['EMA model']
        else:
            EMAmodel = 0 # old versions (< 0.5.0)
            
        if EMAmodel == 0:
            self.EMA_mean.setChecked(True)
        elif EMAmodel == 1:
            self.EMA_Bruggemann.setChecked(True)
        else:
            self.EMA_MaxwellGarnett.setChecked(True)
            
        
        # polarization
        self.polTMRB.setChecked(self.settings['polarization']) # 0 => TE(s) 1 => TM (p)
        
        # others
        self.pathEdit.setText(self.settings['MaterialDBPath'])
        self.loadLastFileCB.setChecked(self.loadLastFile)

    def makeSpectrum(self):
        start = self.settings['wavelengthRange'][0]
        end = self.settings['wavelengthRange'][1]
        step = self.settings['wavelengthRange'][2]
        
        self.settings['wavelength'] = np.arange(start, end + step, step)
    
    @pyqtSlot(int)
    def on_startSB_valueChanged(self, p0):
        self.settings['wavelengthRange'][0] = p0
        self.makeSpectrum()
        
    @pyqtSlot(int)
    def on_endSB_valueChanged(self, p0):
        self.settings['wavelengthRange'][1] = p0
        self.makeSpectrum()
        
    @pyqtSlot(int)
    def on_stepSB_valueChanged(self, p0):
        self.settings['wavelengthRange'][2] = p0
        self.makeSpectrum()
        
    @pyqtSlot()
    def on_pathButton_clicked(self):
        DirName = QFileDialog.getExistingDirectory(self, 'select a folder containing the nk files', os.getcwd()+'\\materialDB')
        if DirName:
            self.pathEdit.setText(DirName)
            self.settings['MaterialDBPath'] = DirName

    @pyqtSlot()
    def on_PathEdit_editingFinished(self):
        if os.path.isdir(self.pathEdit.text()):
            self.settings['MaterialDBPath'] = self.pathEdit.text()
    
    @pyqtSlot()
    def on_reloadButton_clicked(self):
        self.reloadMaterialDB()
    
    @pyqtSlot(bool)
    def on_loadLastFileCB_toggled(self, checked):
        self.loadLastFile = checked
    

    @pyqtSlot(int)
    def on_intensitySlider_valueChanged(self, value):
        self.intensityLabel.setText('{}%'.format(value))
        self.settings['intensity'] = value
    
    @pyqtSlot(int)
    def on_angleSB_valueChanged(self, p0):
        self.settings['angle'] = p0
 
    def fillSpectra(self):
        path = os.getcwd() + '\\spectra'
        included_extenstions = ['dat']
        self.spectraFiles = [fn for fn in os.listdir(path) if any([fn.endswith(ext) for ext in included_extenstions])]
        self.spectra = []
        for i, Mat in enumerate(self.spectraFiles):
            self.spectra.append(Mat.replace('.dat', ''))
        spectraFilePaths = [(path + '\\' + i) for i in self.spectraFiles]
        self.spectraDB = dict(zip(self.spectra,  spectraFilePaths))
        self.spectrumCB.clear()
        self.spectrumCB.addItems(self.spectra)
        
        for name, filepath in self.spectraDB.items():
            if filepath == path + '\\' + self.settings['spectrum']:
                indexStr = name
        index = self.spectrumCB.findText(indexStr)
        self.spectrumCB.setCurrentIndex(index)
        #fg
        
    @pyqtSlot(str)
    def on_spectrumCB_activated(self, p0):
        self.settings['spectrum'] = p0 + '.dat'
    
    @pyqtSlot(bool)
    def on_LBcorrectForReflCB_toggled(self, checked):
        self.settings['LB correct for Reflection'] = checked

    @pyqtSlot(bool)
    def on_gradingAdvancedCB_toggled(self, checked):
        self.settings['grading advanced'] = checked
        
    @pyqtSlot(bool)
    def on_roughEMACB_toggled(self, checked):
        self.settings['roughness EMA model'] = checked
    
    @pyqtSlot(bool)
    def on_roughFresnelCB_toggled(self, checked):
        self.settings['roughness Fresnel model'] = checked
    
    @pyqtSlot(bool)
    def on_EMA_mean_toggled(self, checked):
        self.EMA_update()
    
    @pyqtSlot(bool)
    def on_EMA_Bruggemann_toggled(self, checked):
        self.EMA_update()
    
    @pyqtSlot(bool)
    def on_EMA_MaxwellGarnett_toggled(self, checked):
        self.EMA_update()
    
    def EMA_update(self):
        if self.EMA_mean.isChecked():
            self.settings['EMA model'] = 0
        elif self.EMA_Bruggemann.isChecked():
            self.settings['EMA model'] = 1
        else:
            self.settings['EMA model'] = 2
    
    @pyqtSlot(bool)
    def on_polTERB_toggled(self, checked):
        pol = self.polTMRB.isChecked()
        self.settings['polarization'] = pol
    
    @pyqtSlot(bool)
    def on_polTMRB_toggled(self, checked):
        pol = self.polTMRB.isChecked()
        self.settings['polarization'] = pol
    
    @pyqtSlot(int)
    def on_RaytracerIterationsSB_valueChanged(self, p0):
        self.settings['roughness Haze calc diffuse'][1] = p0
    
    @pyqtSlot(float)
    def on_RaytracerIntensitySB_valueChanged(self, p0):
        self.settings['roughness Haze calc diffuse'][2] = p0
    
    @pyqtSlot(bool)
    def on_calcDiffuseLightCB_toggled(self, checked):
        calcOn = self.calcDiffuseLightCB.isChecked()
        self.settings['roughness Haze calc diffuse'][0] = calcOn
