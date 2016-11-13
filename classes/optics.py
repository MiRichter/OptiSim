'''
Class for stack of layers as used for calculation
'''

import os
import logging
import numpy as np
import scipy as sp
from numpy import cos #, inf, zeros, array, exp, conj
from collections import OrderedDict

from scipy import integrate

from classes.errors import *

def snell(cri1, cri2, theta1):
    '''
    calculates the (complex) angle per wavelength of the light propagation by Snell's law
    '''
    return sp.arcsin(np.real_if_close(cri1*np.sin(theta1) / cri2))
    
def r_ij(polarization, rough, d_rough, wvl, cri_i, cri_j, th_i, th_j):
    """
    reflection amplitude (from Fresnel equations)
    polarization is either "s" or "p" for polarization
    d_rough gives the roughness height of the j-th interface
    cri_i, cri_j are (complex) refractive index for incident and final
    th_i, th_j are (complex) propegation angle for incident and final
    (in radians, where 0=normal). "th" stands for "theta".
    """
    if polarization == 's':
        #return 2 * n_i * cos(th_i) / (n_i * cos(th_i) + n_f * cos(th_f))
        r_jk = ((cri_i * cos(th_i) - cri_j * cos(th_j)) /
                (cri_i * cos(th_i) + cri_j * cos(th_j)))
    elif polarization == 'p':
        r_jk = ((cri_j * cos(th_i) - cri_i * cos(th_j)) /
                (cri_j * cos(th_i) + cri_i * cos(th_j)))
    if rough:
            # r_jk = r_jk(0) * exp(-2(2piZ/lambda)²)
        r_jk = r_jk * np.exp(-2 * (2* np.pi * (d_rough) * cri_i / wvl)**2)
    return r_jk
    
    
    
def t_ij(polarization, rough, d_rough, wvl, cri_i, cri_j, th_i, th_j):
    """
    transmission amplitude (frem Fresnel equations)
    d_rough gives the roughness height of the j-th interface
    """
    if polarization == 's':
        t_jk = 2 * cri_i * cos(th_i) / (cri_i * cos(th_i) + cri_j * cos(th_j))
    elif polarization == 'p':
         t_jk = 2 * cri_i * cos(th_i) / (cri_j * cos(th_i) + cri_i * cos(th_j))
    if rough:
            # r_jk = r_jk(0) * exp(-2(2piZ/lambda)²)
            t_jk = t_jk * np.exp(-0.5 * (2* np.pi * d_rough/wvl)**2 * (cri_j - cri_i)**2)
    return t_jk

class Optics:
    
    def __init__(self, stackname, layerstack, references, settings):
        '''
        Class for calculating the optics of a layerstack
        
        input:
        layer names
        layer thicknesses
        layer cri
        
        
        Output:
            curves:
                spectra:
                + stack A,R,T
                    - absorption
                    - reflection
                    - transmission                
                + absorption (layerwise)
                    - layer 1
                    - layer 2
                    - layer 3 
                    - ...
                + quantum efficiency
                    - internal 
                    - external
                
                profile:
                + light intensity
                + optical generation
                + collected generation
                
                2D:
                + E-field intensity
                + Generation
                
            scalars:
                absorbance - relative total absorption
                relfectance - relative total reflection
                transmittance - relative total transmission
                total generation
                
        '''
       
    
        ''' create dictionary of available plots including lists of 
            - wavelength dependent curves
            - depth dependent curves
        '''
        
        self.availablePlots = OrderedDict([('spectra', {}), 
                                    ('profiles', {}), 
                                    ('2D', {})
                                    ])
        self.scalars = OrderedDict([('absorbance (%)',  0), 
                        ('reflectance (%)', 0),
                        ('transmittance (%)',  0),
                        ('absorbance (mA/cm²)',  0), 
                        ('reflectance (mA/cm²)', 0),
                        ('transmittance (mA/cm²)',  0),
                        ('generated current (mA/cm²)',  0),
                        ('illum. intensity (W/m²)', 0), 
                        ('Jmax (mA/cm²)', 0), 
                        ('absorption layerwise (%) ', []), 
                        ('absorption layerwise (mA/cm²) ', []), 
                        ('collection layerwise (%) ', []), 
                        ('collection layerwise (mA/cm²) ', []), 
                        ('absorbance LB (%)', 0), 
                        ('absorbance LB (mA/cm²)', 0), 
                        ('absorption layerwise LB (%) ', []), 
                        ('absorption layerwise LB (mA/cm²) ', []), 
                        ('collection layerwise LB (%) ', []), 
                        ('collection layerwise LB (mA/cm²) ', []),
                        ('calc. time (s)', 0), 
                        ('creation time (s)', layerstack.creationTime),
                        ('Chi Square R', 0),
                        #('costFunc2', 0),
                        #('costFunc3', 0), 
                        ('Chi Square EQE', 0)
                        #('costFunc2EQE', 0)
                        ])
        self.stackname = stackname
        self.layerstack = layerstack
        self.stack = layerstack.layersequence
        self.wavelength = layerstack.wavelength
        self.names = layerstack.names
        self.thicknesses = layerstack.thicknesses
        self.StackThickness = np.sum(self.thicknesses)
        self.settings = settings
        self.HazeOn = layerstack.HazeOn
        self.calculationOptions = { 'LBcorrection': settings['LB correct for Reflection']
                                    }
        self.rough = settings['roughness Fresnel model']
        self.makeSpectrum()
        
        if settings['polarization']:
            self.pol = 'p'
        else:
            self.pol = 's'
            
        #self.Absorption = self.calcAbsorption()
        #self.TotalAbsorption = 30.3
        
        #self.A, self.R = self.calcSystem()
        
        self.LayerResults = {}
        self.x = []
        t = np.cumsum(self.layerstack.thicknesses)
        
        for i, layer in enumerate(self.stack):
            self.LayerResults[layer.name] = self.stack[i]
            if i == 0:
                self.x.extend(self.LayerResults[layer.name].x)
            else:
                self.x.extend(self.LayerResults[layer.name].x + t[i-1])
        self.x = np.array(self.x)
        
        
        self.references = references
        self.createReferenceCurves()
        #self.calcAllMatrices()
        
        
    def addPlot(self, plotDict, category = 'spectra' , subcategory = 'total A,R,T'):
        if category == '2D':
            self.availablePlots[category].update(plotDict)
            return
        if subcategory in self.availablePlots[category]:
            self.availablePlots[category][subcategory].update(plotDict)
        else:
            self.availablePlots[category][subcategory] = plotDict
            
        
    def createReferenceCurves(self):
        references = self.references
        for name, path in references.items():
            if path[0] is not '':
                logging.info('\tload reference curve {} from {}...'.format(name, path[0]))
                try:
                    rawdata = np.loadtxt(path[0], comments='#')
                except IOError as e:
                    raise LoadError('Could not open {} file: \n {}'.format(name, e.args[1]))
                try:
                    if rawdata[0, 0] < 100: # check if given in mum or nm
                        rawdata[:, 0] = rawdata[:, 0]*1000
                    data = np.interp(self.wavelength, rawdata[:, 0], rawdata[:, 1])
                except: 
                    raise LoadError('Could not interpolate {} file: \n to given spectrum'.format(name))
                if data.mean() > 1: # check if given in %
                    data = data / 100
                if name == 'R reference':
                    self.R_reference = data
                    if path[1]:
                        self.addPlot({name: data}, 'spectra', 'total A,R,T')
                if name == 'T reference' and path[1]:
                    self.addPlot({name: data}, 'spectra', 'total A,R,T')
                    self.T_reference = data
                if name == 'EQE reference' and path[1]:
                    self.addPlot({name: data},'spectra', 'QE')
                    self.EQE_reference = data
                if name == 'psi reference' and path[1]:
                    self.addPlot({name: data}, 'spectra', 'Ellipsometry')
                if name == 'delta reference' and path[1]:
                    self.addPlot({name: data}, 'spectra', 'Ellipsometry')
                    
                    
    def makeSpectrum(self):
        self.loadSpectrum()
        intensity = self.layerstack.intensity
        self.spectrum = self.AM15 * intensity
        
        self.scalars['illum. intensity (W/m²)'] = self.Imax * intensity
        logging.info('\t--> total light intensity is {:.4f} W/m^2'.format(self.Imax))
        logging.info('\t--> scaled light intensity is {:.4f} W/m^2'.format(self.Imax * intensity))
        
    def loadSpectrum(self):
         # Constants
        h = 6.62606957e-34 # Js Planck's constant
#        he = 4.1356675e-15 # eVs
        c = 2.99792458e8 #m/s speed of light
        q = 1.602176e-19 #C electric chargeq 
        self.spectrumFile = self.settings['spectrum']
        SpectrumFile = os.getcwd() + '\\spectra\\' + self.spectrumFile
        logging.info('\tload spectrum file {}...'.format(SpectrumFile))
        data = np.loadtxt(SpectrumFile, comments='>')
        
        self.Imax = np.sum(data[:, 1])
        
        logging.info('\tnormalize total spectrum [W/m^2s] to wavelength-resolved [W/m^2s nm] to allow interpolation...')
        # norm the spectra (2nd column P * dlambda [W/m²s]) to P [W/m²s_nm] by Pdlambda/dlambda with dlambda as (lambda_x+1 - lambda_x-1)/2; first and last seperately
        spec_norm = np.zeros(data.shape[0])
        spec_norm[0] = data[0, 1] / (data[1, 0] - data[0, 0])
        spec_norm[-1] = data[-1, 1] / (data[-1, 0] - data[-1-1, 0])
        for i in range(1, data.shape[0]-1):
            spec_norm[i] = data[i, 1] / ((data[i+1, 0] - data[i-1, 0]) / 2)
            
        self.AM15 = np.interp(self.wavelength, data[:, 0], spec_norm)
        
        logging.info('\tcalculate number of incoming photons per m^2s per wavelength = P / Eph...')
        # number of photons per m²s per wavelength =  P / Eph [1/m²s]
        N_ph_s_wl = self.wavelength * self.AM15 * 1e-9 / (h * c)
        
        # current J_wl = N_ph_s_wl * q --> J = sum(J_wl) A/m² = 0.1 mA/cm²
        logging.info('\tcalculate maximum current Jmax = integr(q * N_ph)...')
        self.spectrumCurrent = N_ph_s_wl * q * 0.1
        self.Jmax = integrate.trapz(self.spectrumCurrent, x=self.wavelength, axis = 0)
        logging.info('\t--> Jmax is {:.4f} mA/cm^2'.format(self.Jmax))
        
        self.scalars['Jmax (mA/cm²)'] = self.Jmax
        
    def calcAllMatrices(self):
        self.setInterfaceMatrices()
        #self.setLayerPartialSystemMatrices()
        self.getSystemMatrix()
            
    def setInterfaceMatrices(self):
        '''
        Interface matrix of interface between each layer with its following
        seperate if IF is coherent (field Fresnel-coefficient) or incoherent (intensity Fresnel-coefficient)
        both are calculated for all layers!!!
        '''
        logging.info('\tcreate interface matrices for all layers...')
        #first interface Air/layer1
        cri_i = np.ones((len(self.wavelength)), np.complex)

        t_jk = t_ij(self.pol, self.rough, self.LayerResults[self.names[0]].sroughThickness, self.wavelength, cri_i, self.LayerResults[self.names[0]].cri,
                    self.layerstack.theta0, self.LayerResults[self.names[0]].theta)
        r_jk = r_ij(self.pol, self.rough, self.LayerResults[self.names[0]].sroughThickness, self.wavelength, cri_i, self.LayerResults[self.names[0]].cri,
                    self.layerstack.theta0, self.LayerResults[self.names[0]].theta)
        t_kj = t_ij(self.pol, self.rough, self.LayerResults[self.names[0]].sroughThickness, self.wavelength, self.LayerResults[self.names[0]].cri, cri_i,
                    self.LayerResults[self.names[0]].theta, self.layerstack.theta0)
        r_kj = r_ij(self.pol, self.rough, self.LayerResults[self.names[0]].sroughThickness, self.wavelength, self.LayerResults[self.names[0]].cri, cri_i,
                     self.LayerResults[self.names[0]].theta, self.layerstack.theta0)
                    

        self.firstInterfaceMatrix = np.zeros((len(self.wavelength), 2, 2), np.complex)
        self.firstInterfaceMatrixInc = np.zeros((len(self.wavelength), 2, 2), np.complex)
        
        if self.LayerResults[self.names[0]].srough:
            hazeR = self.LayerResults[self.names[0]].sroughHazeR
            hazeT = self.LayerResults[self.names[0]].sroughHazeT
        else:
            hazeR = 0
            hazeT = 0
        hazeR = np.sqrt(1-hazeR)
        hazeT = np.sqrt(1-hazeT)
        
        # coherent
        self.firstInterfaceMatrix[:, 0, 0] = 1 / (hazeT * t_jk)
        self.firstInterfaceMatrix[:, 0, 1] = (hazeR * r_jk) / (hazeT * t_jk)
        self.firstInterfaceMatrix[:, 1, 0] = (hazeR * r_jk) / (hazeT * t_jk)
        self.firstInterfaceMatrix[:, 1, 1] =  (hazeT**2 + (hazeR**2 - hazeT**2) * r_jk**2) / (hazeT * t_jk)
        
        # incoherent
        self.firstInterfaceMatrixInc[:, 0, 0] = 1 / np.abs(t_jk)**2
        self.firstInterfaceMatrixInc[:, 0, 1] = - np.abs(r_jk)**2 / np.abs(t_jk)**2
        self.firstInterfaceMatrixInc[:, 1, 0] = np.abs(r_jk)**2 / np.abs(t_jk)**2
        self.firstInterfaceMatrixInc[:, 1, 1] = (np.abs(t_jk * t_kj)**2 - np.abs(r_jk * r_kj)**2) / np.abs(t_jk)**2
            
        for i in range(len(self.names)):
            layer1 = self.LayerResults[self.names[i]]
            if i < len(self.stack)-1:
                layer2 = self.LayerResults[self.names[i+1]]
                # for TE polarized waves
                t_jk = t_ij(self.pol, self.rough, layer2.sroughThickness, self.wavelength, layer1.cri, layer2.cri, layer1.theta, layer2.theta)
                r_jk = r_ij(self.pol, self.rough, layer2.sroughThickness, self.wavelength, layer1.cri, layer2.cri, layer1.theta, layer2.theta)
                t_kj = t_ij(self.pol, self.rough, layer2.sroughThickness, self.wavelength, layer2.cri, layer1.cri, layer2.theta, layer1.theta)
                r_kj = r_ij(self.pol, self.rough, layer2.sroughThickness, self.wavelength, layer2.cri, layer1.cri, layer2.theta, layer1.theta)
                
                layer1.InterfaceMatrix = np.zeros((len(self.wavelength), 2, 2), np.complex)
                layer1.InterfaceMatrixInc = np.zeros((len(self.wavelength), 2, 2), np.complex)
                
                if layer2.srough:
                    hazeR = layer2.sroughHazeR
                    hazeT = layer2.sroughHazeT
                else:
                    hazeR = 0
                    hazeT = 0
                
                hazeR = np.sqrt(1-hazeR)
                hazeT = np.sqrt(1-hazeT)
                #print(hazeR, hazeT)
        
                # coherent
                layer1.InterfaceMatrix[:, 0, 0] = 1 / (hazeT * t_jk)
                layer1.InterfaceMatrix[:, 0, 1] = (hazeR * r_jk) / (hazeT * t_jk)
                layer1.InterfaceMatrix[:, 1, 0] = (hazeR * r_jk) / (hazeT * t_jk)
                layer1.InterfaceMatrix[:, 1, 1] = (hazeT**2 + (hazeR**2 - hazeT**2) * r_jk**2) / (hazeT * t_jk)
                
                # incoherent
                layer1.InterfaceMatrixInc[:, 0, 0] = 1 / np.abs(hazeT * t_jk)**2
                layer1.InterfaceMatrixInc[:, 0, 1] = - np.abs(hazeR * r_jk)**2 / np.abs(hazeT * t_jk)**2
                layer1.InterfaceMatrixInc[:, 1, 0] = np.abs(hazeR * r_jk)**2 / np.abs(hazeT * t_jk)**2
                layer1.InterfaceMatrixInc[:, 1, 1] = (np.abs(hazeT**2 * t_jk * t_kj)**2 - np.abs((hazeR**2 - hazeT**2) * r_jk * r_kj)**2) / np.abs(hazeT * t_jk)**2                    
            
            else:
                #last interface layer1/Air
                self.theta_out = snell(layer1.cri, cri_i, layer1.theta)
                t_jk = t_ij(self.pol, 0, 0, self.wavelength, layer1.cri, cri_i, layer1.theta, self.theta_out)
                r_jk = r_ij(self.pol, 0, 0, self.wavelength, layer1.cri, cri_i, layer1.theta, self.theta_out)
                t_kj = t_ij(self.pol, 0, 0, self.wavelength, cri_i, layer1.cri, self.theta_out, layer1.theta)
                r_kj = r_ij(self.pol, 0, 0, self.wavelength, cri_i, layer1.cri, self.theta_out, layer1.theta)
                
                layer1.InterfaceMatrix = np.zeros((len(self.wavelength), 2, 2), np.complex)
                layer1.InterfaceMatrixInc = np.zeros((len(self.wavelength), 2, 2), np.complex)
                # coherent
                layer1.InterfaceMatrix[:, 0, 0] = layer1.InterfaceMatrix[:, 1, 1] = 1 / t_jk
                layer1.InterfaceMatrix[:, 0, 1] = layer1.InterfaceMatrix[:, 1, 0] = r_jk / t_jk
                # incoherent
                layer1.InterfaceMatrixInc[:, 0, 0] = 1 / np.abs(t_jk)**2
                layer1.InterfaceMatrixInc[:, 0, 1] = - np.abs(r_jk)**2 / np.abs(t_jk)**2
                layer1.InterfaceMatrixInc[:, 1, 0] = np.abs(r_jk)**2 / np.abs(t_jk)**2
                layer1.InterfaceMatrixInc[:, 1, 1] = (np.abs(t_jk * t_kj)**2 - np.abs(r_jk * r_kj)**2) / np.abs(t_jk)**2                    
            
    def getSystemMatrix(self):
        '''
               m
            ------
             |  |
        S =[ |  | I_(v-1),v L_v] I_(m,m+1)
             |  |
             v = 1 
        every layer has a coherent (Field value) AND incoherent (intensity value) layer and interface matrix, here the one that is needed (= thick) is taken
        seperate between stack of coherent layers (Field) and incoherent layers (Int) in between:
        first calc all coherent stacks take the and
        '''
        logging.info('\tcreate partial system matrices for each layer...')
        
        for j, key in enumerate(self.names):
            self.LayerResults[key].PSI_Field = np.zeros((len(self.wavelength), 2, 2), np.complex)
            self.LayerResults[key].PSO_Field = np.zeros((len(self.wavelength), 2, 2), np.complex)
            self.LayerResults[key].PSI_Int = np.zeros((len(self.wavelength), 2, 2), np.complex)
            self.LayerResults[key].PSO_Int = np.zeros((len(self.wavelength), 2, 2), np.complex)
            
        self.SystemFieldMatrix = np.zeros((len(self.wavelength), 2, 2), np.complex) # complete coherent (no "thick") --> required for Ellipsometry
        self.SystemIntMatrix = np.zeros((len(self.wavelength), 2, 2), np.complex) # complete incoherent (all "thick") 
        
        self.SystemMatrix = np.zeros((len(self.wavelength), 2, 2), np.complex) # mixture of both - coherent and incoherent - as required
        
        self.WhatComesOut = np.zeros(len(self.wavelength))
        
        logging.info('\tcreate system matrix...') # acutally PSI and PSO are not ready yet
        
        for wvl in range(len(self.wavelength)):
            # first interface
            SysMatCoh = self.firstInterfaceMatrix[wvl]
            SysMatInc = self.firstInterfaceMatrixInc[wvl]
            if not self.LayerResults[self.names[0]].thick:
                SysMat = SysMatCoh
            else:
                SysMat = SysMatInc
            
            # calc a complete coherent and incoherent stack: 
            for name in self.names:
                #coherent
                IfMat = self.LayerResults[name].InterfaceMatrix[wvl]
                LMat = self.LayerResults[name].LayerMatrix[wvl]
                SysMatCoh = np.dot(SysMatCoh, np.dot(LMat, IfMat)) # doesn't matter if matrix elements are kept field Fresnel and A,R,T are calculated with abs(...)^2 or if elements are tranferred to intensity matrix, e.g., abs(S00)^2
                # incoherent
                IfMatInc = self.LayerResults[name].InterfaceMatrixInc[wvl]
                LMatInc = self.LayerResults[name].LayerMatrixInc[wvl]
                SysMatInc = np.dot(SysMatInc, np.dot(LMatInc, IfMatInc))
            
            self.SystemFieldMatrix[wvl] = SysMatCoh         # complete coherent (no "thick")
            self.SystemIntMatrix[wvl] = SysMatInc  # complete incoherent (all "thick") 
           
            # calc all coherent parts and make a List of them
            coherentParts = []
            incoherentLayers = []
            for i, name in enumerate(self.names):
                IfMat = self.LayerResults[name].InterfaceMatrix[wvl]
                LMat = self.LayerResults[name].LayerMatrix[wvl]
                if not self.LayerResults[name].thick:
                    if i == 0:
                        SysMat = self.firstInterfaceMatrix[wvl]
                    elif self.LayerResults[self.names[i-1]].thick:
                        SysMat = self.LayerResults[self.names[i-1]].InterfaceMatrix[wvl]
                    # create E-field partial system matrices for this coherent part (later Intensity matrices added)
                    self.LayerResults[name].PSI_Field[wvl] = SysMat
                    self.LayerResults[name].PSO_Field[wvl] = IfMat
                    # go through next coherent layers to get partial system matrix out for this coherent part
                    for j in range(i+1, len(self.names)):
                        if not self.LayerResults[self.names[j]].thick:
                            LMatPart = self.LayerResults[self.names[j]].LayerMatrix[wvl]
                            IfMatPart = self.LayerResults[self.names[j]].InterfaceMatrix[wvl]
                            self.LayerResults[name].PSO_Field[wvl] =  np.dot(self.LayerResults[name].PSO_Field[wvl], np.dot(LMatPart, IfMatPart))
                        else:
                            break
                            
                    SysMat = np.dot(SysMat, np.dot(LMat, IfMat))
                    if i == len(self.names)-1:
                        # last layer
                        coherentParts.append(SysMat)
                else:
                    incoherentLayers.append(i)
                    if i > 0 and not self.LayerResults[self.names[i-1]].thick:
                        coherentParts.append(SysMat)

            #calc all interfaceIntensityMatrices of the coherent parts in the list
            coherentPartsIntensity = []
            for part in coherentParts:
                S00 = part[0, 0]
                S01 = part[0, 1]
                S10 = part[1, 0]
                #S11 = part[1, 1]
                detS = np.linalg.det(part)
                
                partIntensity = np.zeros((2, 2), np.complex)
                
                partIntensity[0, 0] = np.abs(S00)**2
                partIntensity[0, 1] = - np.abs(S01)**2
                partIntensity[1, 0] = np.abs(S10)**2
                partIntensity[1, 1] = (np.abs(detS)**2 - np.abs(S01 * S10)**2) / np.abs(S00)**2
                
                coherentPartsIntensity.append(partIntensity)
            
            
            startswithcoherent = False
            currentCoherentPart = 0
            if incoherentLayers:
                if incoherentLayers[0] == 0:
                    SysMat = self.firstInterfaceMatrixInc[wvl]
                else:
                    SysMat = coherentPartsIntensity[0]
                    startswithcoherent = True
                    currentCoherentPart += 1
                    
                for i, incLayer in enumerate(incoherentLayers):
                    IfMatInc = self.LayerResults[self.names[incLayer]].InterfaceMatrixInc[wvl]
                    LMatInc = self.LayerResults[self.names[incLayer]].LayerMatrixInc[wvl]
                    
                    if incLayer < len(self.names)-1:
                        if self.LayerResults[self.names[incLayer+1]].thick:
                            IfMat = IfMatInc
                        else:
                            IfMat = coherentPartsIntensity[currentCoherentPart]
                            currentCoherentPart += 1
                    else: # last layer
                        IfMat = IfMatInc
                        
                    # go through next intensity (parts) layers
                    self.LayerResults[self.names[incLayer]].PSI_Int[wvl] = SysMat
                    self.LayerResults[self.names[incLayer]].PSO_Int[wvl] = IfMat
                    for j in range(i+1, len(incoherentLayers)):
                        LMatPart = self.LayerResults[self.names[j]].LayerMatrixInc[wvl]
                        if j < len(incoherentLayers)-1:
                            if self.LayerResults[self.names[j+1]].thick:
                                IfMatPart = self.LayerResults[self.names[j]].InterfaceMatrixInc[wvl]
                            #elif startswithcoherent:
                            #    IfMatPart = coherentPartsIntensity[i+j+1]
                            else:
                
                                IfMatPart = coherentPartsIntensity[currentCoherentPart] #i+j
                        else:
                            IfMatPart = self.LayerResults[name].InterfaceMatrixInc[wvl]
                        self.LayerResults[name].PSO_Int[wvl] =  np.dot(self.LayerResults[name].PSO_Int[wvl], np.dot(LMatPart, IfMatPart))
                    SysMat = np.dot(SysMat, np.dot(LMatInc, IfMat))
            else:
                SysMat = coherentPartsIntensity[0]
            self.SystemMatrix[wvl] = SysMat
            
            self.WhatComesOut[wvl] = np.abs(1 / self.SystemMatrix[wvl, 0, 0])
            
            # go through all coherent layers and add PSI and PSO from incoherent parts 
            for k, name in enumerate(self.names):
                if self.LayerResults[name].thick:
                    pass
                else:
                    if k == 0:
                        pass
                    else:
                        if self.LayerResults[self.names[k-1]].thick:
                            # Take PSI from previous incoherent layer and add LayerMatrix of it
                            PSI = np.dot(self.LayerResults[self.names[k-1]].PSI_Int[wvl], self.LayerResults[self.names[k-1]].LayerMatrixInc[wvl])
                            # loop through next coherent layers
                            coh = k
                            cohLayers = []
                            while coh < len(self.names) and not self.LayerResults[self.names[coh]].thick:
                                # add PSI to all coherent layers in this coherent stack
                                self.LayerResults[self.names[coh]].PSI_Field[wvl] = np.dot(np.sqrt(PSI), self.LayerResults[self.names[coh]].PSI_Field[wvl])
                                # save which layers are in this part
                                cohLayers.append(self.names[coh])
                                coh += 1
                            if coh < len(self.names):
                                for cohName in cohLayers:
                                    LMat = np.sqrt(self.LayerResults[self.names[coh]].LayerMatrixInc[wvl])
                                    IfMat = np.sqrt(self.LayerResults[self.names[coh]].PSO_Int[wvl])
                                    self.LayerResults[cohName].PSO_Field[wvl] = np.dot(self.LayerResults[cohName].PSO_Field[wvl], LMat) 
                                    self.LayerResults[cohName].PSO_Field[wvl] = np.dot(self.LayerResults[cohName].PSO_Field[wvl], IfMat) 

        
            
    def calcDiffuseLight(self):
        '''
        go through all layers and get the diffuse parts 
        of forward and backwards moving waves 
        from at each interface as starting for raytracong the diffuse light
  
        the specular part of light intensity going 
        forward to an interface I_spec_fw and
        going backwards to an interface I_spec_bw are required 
        from this with Haze_r and Haze_t the diffuse parts I_diff_fw and I_diff_bw are calculated
        
        '''
        '''
        get the E-field intensity for each layer at the positions:
            | --> I_fw(x0)     I_fw(xend)-->|
            |                               |
            |                               |
            |<-- I_bw(x0)      I_bw(xend)-->|
        
        see Petterson et al. JAP 86
        '''
        logging.info('\tcalculate diffusive light...')
        wvl = self.wavelength
        
        for k, key in enumerate(self.names):
            if not self.LayerResults[key].thick:
                # get previous layer for I_spec_fw at left side of Top-Interface 
                PSI_Field = self.LayerResults[key].PSI_Field
                PSO_Field = self.LayerResults[key].PSO_Field
            else:
                # get previous layer for I_spec_fw at left side of Top-Interface 
                PSI_Field = np.sqrt(self.LayerResults[key].PSI_Int)
                PSO_Field = np.sqrt(self.LayerResults[key].PSO_Int)
            
            xi = self.LayerResults[key].xi
            t = self.LayerResults[key].thickness
            EXP = 1j * xi * t
            r_l = - PSI_Field[:, 0, 1] / PSI_Field[:, 0, 0]
            r_ll = PSO_Field[:, 1, 0] / PSO_Field[:, 0, 0]
            t_l = 1 / PSI_Field[:, 0, 0]
            t_fw = t_l / (1-r_l * r_ll * np.exp(2*EXP))
            t_bw = t_fw * r_ll * np.exp(2*EXP)
            n = self.LayerResults[key].n
            
            self.LayerResults[key].I_fw_start = n * np.abs(t_fw)**2
            self.LayerResults[key].I_fw_end = n * np.abs(t_fw * np.exp(EXP))**2 
            self.LayerResults[key].I_bw_start = n * np.abs(t_bw * np.exp(-EXP))**2
            #self.LayerResults[key].I_bw_end = np.abs(t_bw)**2 
        
        for k, key in enumerate(self.names):
            ''' calculate diffused light as
            
            layer0              layer1                          layer2
             I_fw0(end)->|--> I_fw_diff_t     I_bw_diff_t <--|<- I_bw2(x0)
                         |                                   |
                         |<-  I_bw1(x0)       I_fw1(xend)  ->|
                         |--> I_fw_diff_r     I_bw_diff_r <--|
            
            I_fw_diff_t = H_T01 * T_01 * I_fw0(xend)
            I_fw_diff_r = H_R01 * R_10 * I_bw1(x0)
            I_bw_diff_t = H_T12 * T_21 * I_bw2(x0)
            I_bw_diff_r = H_R12 * R_12 * I_fw1(xend)    
                correct?
            '''
            if self.LayerResults[key].srough:
                H_R01 = self.LayerResults[key].sroughHazeR
                H_T01 = self.LayerResults[key].sroughHazeT
            else:
                H_R01 = 0
                H_T01 = 0
                
            #print('H_T_{} = {}'.format(key, H_T01))
            if k == 0:
                cri0 = 1 + 0j
                theta0 = self.layerstack.theta0
            else:
                cri0 = self.LayerResults[self.names[k-1]].cri
                theta0 = self.LayerResults[self.names[k-1]].theta
            cri1 = self.LayerResults[key].cri 
            theta1 = self.LayerResults[key].theta
            if k == len(self.names)-1: # last layer
                cri2 = 1 + 0j
                theta2 = self.theta_out
                H_R12 = 0
                H_T12 = 0
            else:
                cri2 = self.LayerResults[self.names[k+1]].cri
                theta2 = self.LayerResults[self.names[k+1]].theta
                if self.LayerResults[self.names[k+1]].srough:
                    H_R12 = self.LayerResults[self.names[k+1]].sroughHazeR
                    H_T12 = self.LayerResults[self.names[k+1]].sroughHazeT
                else:
                    H_R12 = 0
                    H_T12 = 0
                
            R_01 = np.abs(r_ij(self.pol, 0, 0, wvl, cri0, cri1, theta0, theta1))**2
            T_01 = 1 - R_01
            R_10 = np.abs(r_ij(self.pol, 0, 0, wvl, cri1, cri0, theta1, theta0))**2
            R_21 = np.abs(r_ij(self.pol, 0, 0, wvl, cri2, cri1, theta2, theta1))**2
            T_21 = 1 - R_21
            R_12 = np.abs(r_ij(self.pol, 0, 0, wvl, cri1, cri2, theta1, theta2))**2
            
            self.LayerResults[key].I_fw_diff_r = H_R01 * R_10 * self.LayerResults[key].I_bw_start
            
                
            self.LayerResults[key].I_bw_diff_r = H_R12 * R_12 * self.LayerResults[key].I_fw_end
            #print('T01 of layer {} is {}'.format(k, T_01))
            #print('H01 of layer {} is {}'.format(k, H_T01))


            if k == 0:
                #save first interface reflection
                self.RspectrumDiffuse = H_R01 * R_01 * np.ones(len(wvl))
                #self.LayerResults[key].I_fw_diff_t = ((H_T01 * T_01) / (1 - H_T01)) * self.LayerResults[key].I_fw_start # np.ones(len(self.wavelength)) # first interface: complete light
                self.LayerResults[key].I_fw_diff_t = H_T01 * T_01 * np.ones(len(wvl))  #- self.RspectrumDiffuse)
            else:
                self.LayerResults[key].I_fw_diff_t = H_T01 * T_01 * self.LayerResults[self.names[k-1]].I_fw_end
                #self.LayerResults[key].I_fw_diff_t = ((H_T01 * T_01) / (1 - H_T01)) * self.LayerResults[key].I_fw_start
            
            if k == len(self.names)-1: # last layer
                self.LayerResults[key].I_bw_diff_t = np.zeros(len(self.wavelength)) # no light from backside
            else:
                self.LayerResults[key].I_bw_diff_t = H_T12 * T_21 * self.LayerResults[self.names[k+1]].I_bw_start
                
            
        #fgfdg
        '''
        calculates the total and local intensity of diffuse light by raytracing
        I_fw[layer] 
        I_bw[layer]
        
        I_bw[0] is total reflection
        I_fw[end + 1] is total transmission
        '''
        #self.RspectrumDiffuse = np.zeros(len(wvl)) --> defined already
        self.TspectrumDiffuse = np.zeros(len(wvl))
        
        #create empty variables
        for key in self.names:
            x = self.LayerResults[key].x
            self.LayerResults[key].I_fw_diff_vector = np.zeros((len(x), len(wvl)))
            self.LayerResults[key].I_bw_diff_vector = np.zeros((len(x), len(wvl)))
    
        i = 1
        Imax = 1
        max_stack = 0
        max_before = 0
        logging.info('\t\tstart raytracing...')
        while True:
            if i > self.settings['roughness Haze calc diffuse'][1]:
                logging.info('\t\t\tmaximum number of iterations reached ({})'.format(i))
                #print('maximum number of iterations reached ({})'.format(i))
                break
            if Imax < self.settings['roughness Haze calc diffuse'][2]:
                logging.info('\t\t\tminmum Intensity below threshold after {} iterations'.format(i))
                #print('minmum Intensity below threshold after {} iterations'.format(i))
                break
            for n, key in enumerate(self.names):
                alpha = self.LayerResults[key].alpha
                x = self.LayerResults[key].x
                EXP1 = x[:, np.newaxis]
                t = self.LayerResults[key].thickness
                EXP2 = t - x[:, np.newaxis]
                
                I_fw_start = self.LayerResults[key].I_fw_diff_t + self.LayerResults[key].I_fw_diff_r
                I_bw_start = self.LayerResults[key].I_bw_diff_t + self.LayerResults[key].I_bw_diff_r
                
                I_fw_vector = I_fw_start * np.exp(-alpha*EXP1) # 30° angle scattering / np.cos(np.radians(30))
                I_bw_vector = I_bw_start * np.exp(-alpha*EXP2)
                
                self.LayerResults[key].I_fw_diff_vector = self.LayerResults[key].I_fw_diff_vector + I_fw_vector
                self.LayerResults[key].I_bw_diff_vector = self.LayerResults[key].I_bw_diff_vector + I_bw_vector
                
                # get reflections and transmission for input in next loop
                I_fw_end = I_fw_vector[-1]
                I_bw_end = I_bw_vector[0]
                
                I_fw_max = np.amax(I_fw_end)
                I_bw_max = np.amax(I_bw_end)
                max = np.amax([I_fw_max, I_bw_max])
                if max > max_before:
                    max_stack = max
                
                max_before = max
                
                '''
                    layer 0                 layer 1                         layer 2
                               ->|--> I_fw_diff_t     I_bw_diff_t <--|<--
                                  |                                              |
          I_bw_diff_t (R) <-|<-  I_bw_end                        ->|-> I_fw_diff_t
                                  |--> I_fw_diff_r     I_bw_diff_r <--|
                '''
                
                if n == 0:
                    cri0 = 1 + 0j
                    theta0 = self.layerstack.theta0
                else:
                    cri0 = self.LayerResults[self.names[n-1]].cri
                    theta0 = self.LayerResults[self.names[n-1]].theta
                
                cri1 = self.LayerResults[key].cri 
                theta1 = self.LayerResults[key].theta
                
                if n == len(self.names)-1:
                    cri2 = 1 + 0j
                    theta2 = self.theta_out
                else:
                    cri2 = self.LayerResults[self.names[n+1]].cri
                    theta2 = self.LayerResults[self.names[n+1]].theta
                    
                R_12 = np.abs(r_ij(self.pol, 0, 0, wvl, cri1, cri2, theta1, theta2))**2
                T_12 = 1 - R_12
                R_10 = np.abs(r_ij(self.pol, 0, 0, wvl, cri1, cri0, theta1, theta0))**2
                T_10 = 1 - R_10
                
                I_fw_end_r = I_fw_end * R_12
                I_fw_end_t = I_fw_end * T_12
                I_bw_end_r = I_bw_end * R_10
                I_bw_end_t = I_bw_end * T_10
                
                self.LayerResults[key].I_fw_diff_t = np.zeros(len(wvl)) # filled in previous loop 
                self.LayerResults[key].I_bw_diff_t = np.zeros(len(wvl)) # filled in next loop
                self.LayerResults[key].I_fw_diff_r = I_bw_end_r
                self.LayerResults[key].I_bw_diff_r = I_fw_end_r
                
                if n == 0: # first layer
                    self.RspectrumDiffuse = self.RspectrumDiffuse + I_bw_end_t
                else:
                    self.LayerResults[self.names[n-1]].I_bw_diff_t = I_bw_end_t 
                    
                if n == len(self.names)-1: # last layer
                    self.TspectrumDiffuse = self.TspectrumDiffuse + I_fw_end_t
                else:
                    self.LayerResults[self.names[n+1]].I_fw_diff_t = self.LayerResults[self.names[n+1]].I_fw_diff_t + I_fw_end_t

            if Imax > max_stack:
                Imax = max_stack
            i += 1
        
        # create final result   
        self.I_diffuse = []
        self.I_diffuse_x = []
        
        for key in self.names:
            self.LayerResults[key].I_diffuse = self.LayerResults[key].I_fw_diff_vector - self.LayerResults[key].I_bw_diff_vector 
            self.I_diffuse.extend(self.LayerResults[key].I_diffuse)
            self.I_diffuse_x.extend(integrate.trapz(self.I_diffuse, x=wvl, axis = 1))
           
    
    def setLayerPartialSystemMatrices(self):
        '''
        partial system transfer matrix for field from top to layer j:
             j - 1
            ------
             |  |
        Sin=[|  | I_(v-1) L_v] I_(j-1),j
             |  |
             v = 1
                 
        partial transfer matrix for field from layer j to bottom (m):
              m
            ------
             |  |
       Sout=[|  | I_(v-1) L_v] I_(m,m+1)
             |  |
            v =j+1 
            
        for thick layers: Sin and Sout are Intensity matrices    
        '''
        for j, key in enumerate(self.names):
            self.LayerResults[key].PartSysMatIn = np.zeros((len(self.wavelength), 2, 2), np.complex)
            self.LayerResults[key].PartSysMatOut = np.zeros((len(self.wavelength), 2, 2), np.complex)
            
            for wvl in range(len(self.wavelength)):
                # first interface
                PSI = self.firstInterfaceMatrix[wvl]
                PSO = self.LayerResults[key].InterfaceMatrix[wvl]
                    
                # top to layer (Sin):
                if j > 0:
                    for l in range(j):    # range(j) = 1,...,j-1
                        IfMatI = self.LayerResults[self.names[l]].InterfaceMatrix[wvl]
                        LMatI = self.LayerResults[self.names[l]].LayerMatrix[wvl]
                        PSI = np.dot(PSI, np.dot(LMatI, IfMatI))
                self.LayerResults[key].PartSysMatIn[wvl] = PSI
                    
                # layer to bottom (Sout):
                if j < len(self.names):
                    for m in range(j+1, len(self.names)): # j+1,...,last layer
                        IfMatO = self.LayerResults[self.names[m]].InterfaceMatrix[wvl]
                        LMatO = self.LayerResults[self.names[m]].LayerMatrix[wvl]
                        PSO = np.dot(PSO, np.dot(LMatO, IfMatO))
                self.LayerResults[key].PartSysMatOut[wvl] = PSO
    
    
    def calcEllipsometry(self):
        logging.info('\tcalculate ellipsometric angles...')
        rs = np.zeros((len(self.wavelength)), np.complex)
        rp = np.zeros((len(self.wavelength)), np.complex)
        
        # calc 's' polarization
        self.pol = 's'
        self.setInterfaceMatrices()
        self.getSystemMatrix()
            
        for wvl in range(len(self.wavelength)):
            S21 = self.SystemFieldMatrix[wvl, 1, 0]
            S11 = self.SystemFieldMatrix[wvl, 0, 0]
            rs[wvl] = S21/S11
           
        # calc 'p' polarization
        self.pol = 'p' 
        self.setInterfaceMatrices()
        self.getSystemMatrix()
            
        for wvl in range(len(self.wavelength)):
            S21 = self.SystemFieldMatrix[wvl, 1, 0]
            S11 = self.SystemFieldMatrix[wvl, 0, 0]
            rp[wvl] = S21/S11
        
        degree = np.pi/180
        self.psi = np.arctan(abs(rp/rs))/degree
        self.delta = np.angle(-rp/rs)/degree
        
        self.addPlot({'psi': self.psi}, 'spectra','Ellipsometry')
        self.addPlot({'Delta': self.delta}, 'spectra','Ellipsometry')
        
        if self.settings['polarization']:
            self.pol = 'p'
        else:
            self.pol = 's'
            
        logging.info('\tcalculation of ellipsometric angles finished.')

    def calcStack(self):
        '''
        calculates Stack total absorption, reflection, and transmission
        here you can calc the values (plots and scalars for mixed system or seperate complete coherent or incoherent
        commment out what is not needed
        '''
        self.setInterfaceMatrices()
        self.getSystemMatrix()
            
        if self.HazeOn:
            self.calcDiffuseLight()
        
        logging.info('\tcalculate stack optics...')
        # combined coh and incoherent
        self.RspectrumSystem = np.zeros((len(self.wavelength), 1))
        self.TspectrumSystem = np.zeros((len(self.wavelength), 1))
        self.AspectrumSystem = np.zeros((len(self.wavelength), 1))
        
        # clac complete coherent stack
#        self.AspectrumField = np.zeros((len(self.wavelength), 1))
#        self.RspectrumField = np.zeros((len(self.wavelength), 1))
#        self.TspectrumField = np.zeros((len(self.wavelength), 1))
        
        # clac complete incoh stack
#        self.RspectrumInt = np.zeros((len(self.wavelength), 1))
#        self.TspectrumInt = np.zeros((len(self.wavelength), 1))
#        self.AspectrumInt = np.zeros((len(self.wavelength), 1))
        
        for wvl in range(len(self.wavelength)):
            S10System = self.SystemMatrix[wvl, 1, 0]
            S00System = self.SystemMatrix[wvl, 0, 0]
            self.RspectrumSystem[wvl] = np.abs(S10System / S00System)
            self.TspectrumSystem[wvl] = np.abs(1 / S00System)
            self.AspectrumSystem[wvl] = 1 - (self.TspectrumSystem[wvl] + self.RspectrumSystem[wvl])
            
#            S10 = self.SystemFieldMatrix[wvl, 1, 0]
#            S00 = self.SystemFieldMatrix[wvl, 0, 0]
#            self.RspectrumField[wvl] = np.abs(S10/S00)**2
#            self.TspectrumField[wvl] = np.abs(1/S00)**2
#            self.AspectrumField[wvl] = 1 - (self.Tspectrum[wvl] + self.Rspectrum[wvl])
#            
#            S10Int = self.SystemIntMatrix[wvl, 1, 0]
#            S00Int = self.SystemIntMatrix[wvl, 0, 0]
#            self.RspectrumInt[wvl] = np.abs(S10Int / S00Int)
#            self.TspectrumInt[wvl] = np.abs(1 / S00Int)
#            self.AspectrumInt[wvl] = 1 - (self.TspectrumInt[wvl] + self.RspectrumInt[wvl])
            
        
        if self.HazeOn:
            # here add diffuse part of light Rtot = Rspec + Rdiff; Ttot = Tspec + Tdiff
            self.RspectrumSystem = self.RspectrumSystem[:, 0] + self.RspectrumDiffuse
            self.TspectrumSystem = self.TspectrumSystem[:, 0] + self.TspectrumDiffuse
            self.AspectrumSystem = 1 - (self.TspectrumSystem + self.RspectrumSystem)
            self.addPlot({'absorption diffuse': 1 - (self.TspectrumDiffuse + self.RspectrumDiffuse)})
            self.addPlot({'reflection diffuse': self.RspectrumDiffuse})
            self.addPlot({'transmission diffuse': self.TspectrumDiffuse})
        else:
            self.RspectrumSystem = self.RspectrumSystem[:, 0]
            self.TspectrumSystem = self.TspectrumSystem[:, 0]
            self.AspectrumSystem = self.AspectrumSystem[:, 0]
            
            
        lengthWvl = self.wavelength[-1] - self.wavelength[0]
        
        AnumSys = integrate.trapz(self.AspectrumSystem, x = self.wavelength, axis=0) / lengthWvl
        RnumSys = integrate.trapz(self.RspectrumSystem, x = self.wavelength, axis=0) / lengthWvl
        TnumSys = integrate.trapz(self.TspectrumSystem, x = self.wavelength, axis=0) / lengthWvl
        
#        AnumField = integrate.trapz(self.AspectrumField, x = self.wavelength, axis=0) / lengthWvl
#        RnumField = integrate.trapz(self.RspectrumField, x = self.wavelength, axis=0) / lengthWvl
#        TnumField = integrate.trapz(self.TspectrumField, x = self.wavelength, axis=0) / lengthWvl
#        
#        AnumInt = integrate.trapz(self.AspectrumInt, x = self.wavelength, axis=0) / lengthWvl
#        RnumInt = integrate.trapz(self.RspectrumInt, x = self.wavelength, axis=0) / lengthWvl
#        TnumInt = integrate.trapz(self.TspectrumInt, x = self.wavelength, axis=0) / lengthWvl
        
        self.addPlot({'absorption': self.AspectrumSystem})
        self.addPlot({'reflection': self.RspectrumSystem})
        self.addPlot({'transmission': self.TspectrumSystem})
        
        # calc deviation from reference
        if 'R reference' in self.references:
           # costFunc1 = np.sum(((self.R_reference-self.RspectrumSystem))**2)
          #  costFunc2 = np.sum((self.RspectrumSystem*(self.R_reference-self.RspectrumSystem))**2)            
            costFunc3 = np.sum(((self.RspectrumSystem - self.R_reference)/self.R_reference)**2)
            self.scalars['Chi Square R'] = costFunc3 
        
        self.scalars['absorbance (%)'] = AnumSys * 100 #'%.4f' % 
        self.scalars['reflectance (%)'] = RnumSys * 100
        self.scalars['transmittance (%)'] = TnumSys * 100
                     
        
        #self.scalars['costFunc2'] = costFunc2  
        #self.scalars['costFunc3'] = costFunc3 
        
        # the following is not correct,  because it depends on spectrum
        #self.scalars['absorbance (mA/cm²)'] = AnumSys * self.Jmax 
        #self.scalars['reflectance (mA/cm²)'] = RnumSys * self.Jmax 
        #self.scalars['transmittance (mA/cm²)'] = TnumSys * self.Jmax
        
        self.scalars['absorbance (mA/cm²)'] = integrate.trapz(self.AspectrumSystem * self.spectrumCurrent, x = self.wavelength, axis=0) 
        self.scalars['reflectance (mA/cm²)'] = integrate.trapz(self.RspectrumSystem * self.spectrumCurrent, x = self.wavelength, axis=0)
        self.scalars['transmittance (mA/cm²)'] = integrate.trapz(self.TspectrumSystem * self.spectrumCurrent, x = self.wavelength, axis=0)
        
        logging.info('\tcalculation of stack optics finished.')
#        self.scalars['absorbance incoh(%)'] = AnumInt[0] * 100 #'%.4f' % 
#        self.scalars['reflectance incoh(%)'] = RnumInt[0] * 100
#        self.scalars['transmittance incoh(%)'] = TnumInt[0] * 100
#        
#        self.scalars['absorbance coh(%)'] = AnumField[0] * 100 #'%.4f' % 
#        self.scalars['reflectance coh(%)'] = RnumField[0] * 100
#        self.scalars['transmittance coh(%)'] = TnumField[0] * 100
        
    def calcFieldIntensity(self):
        logging.info('\tcalculate local field intensity...')
        Esquare = []
        EsquareDiffuse = []
        EsquareSpecular = []
        for key in self.names:
            xi = self.LayerResults[key].xi
            t = self.LayerResults[key].thickness
            x = self.LayerResults[key].x
            EXP1 = 1j * xi * (t - x[:, np.newaxis])
            EXP2 = 1j * xi * t
            n = self.LayerResults[key].n
            
            if not self.LayerResults[key].thick:
                PSI_Field = self.LayerResults[key].PSI_Field
                PSO_Field = self.LayerResults[key].PSO_Field
                self.LayerResults[key].E_Field = (PSO_Field[:, 0, 0] * np.exp(-EXP1) + PSO_Field[:, 1, 0] * np.exp(EXP1)) / (PSI_Field[:, 0, 0] * PSO_Field[:, 0, 0] * np.exp(-EXP2)+ PSI_Field[:, 0, 1] * PSO_Field[:, 1, 0] * np.exp(EXP2))
                self.LayerResults[key].Esquare = n * np.abs(self.LayerResults[key].E_Field)**2 
                
            else:
                # eqn. 18-20 Jung et al. JAP 50 (2011)
                PSI_Int = self.LayerResults[key].PSI_Int
                PSO_Int = self.LayerResults[key].PSO_Int
                self.LayerResults[key].Esquare = n * (PSO_Int[:, 0, 0] * np.abs(np.exp(-EXP1))**2 + PSO_Int[:, 1, 0] * np.abs(np.exp(EXP1))**2) / (PSI_Int[:, 0, 0] * PSO_Int[:, 0, 0] * np.abs(np.exp(-EXP2))**2+ PSI_Int[:, 0, 1] * PSO_Int[:, 1, 0] * np.abs(np.exp(EXP2))**2)
            
            if self.HazeOn:
                self.LayerResults[key].EsquareSpecular = self.LayerResults[key].Esquare
                self.LayerResults[key].Esquare = self.LayerResults[key].Esquare + self.LayerResults[key].I_diffuse
                
            Esquare.extend(self.LayerResults[key].Esquare)
            if self.HazeOn:
                EsquareDiffuse.extend(self.LayerResults[key].I_diffuse)
                EsquareSpecular.extend(self.LayerResults[key].EsquareSpecular)

        self.Esquare = np.array(np.abs(Esquare))
        self.EsquareProfile = integrate.trapz(self.Esquare, x=self.wavelength, axis=1) / (self.wavelength[-1] - self.wavelength[0]) # TODO: normalize ? or with spectrum ?
        self.addPlot({'E-field intensity' : self.Esquare}, '2D')
        self.addPlot({'passing light' : self.EsquareProfile}, 'profiles', 'E-field intensity')
        
        if self.HazeOn:
            self.EsquareDiffuse = np.array(EsquareDiffuse)
            self.EsquareSpecular = np.array(EsquareSpecular)
            
            self.EsquareProfileDiffuse = integrate.trapz(self.EsquareDiffuse, x=self.wavelength, axis=1) / (self.wavelength[-1] - self.wavelength[0]) # TODO: normalize ? or with spectrum ?
            self.EsquareProfileSpecular = integrate.trapz(self.EsquareSpecular, x=self.wavelength, axis=1) / (self.wavelength[-1] - self.wavelength[0]) # TODO: normalize ? or with spectrum ?
            self.addPlot({'passing light diffuse' : self.EsquareProfileDiffuse}, 'profiles', 'E-field intensity')
            self.addPlot({'passing light specular' : self.EsquareProfileSpecular}, 'profiles', 'E-field intensity')
            
        logging.info('\tcalculation of field intensity finished.')
        
    def calcAbsorption(self):
        '''
        abs(E-field)^2
        I (mW/cm²nm): relative absorbed light intensity
        '''
        logging.info('\tcalculate layerwise absorption...')
        self.integrAbsorption = {}
        absorptionCurves = {}
        self.absorbedIntensity = []
        wvl = self.wavelength
        
        for key in self.names:
            x = self.LayerResults[key].x
            #TODO: Is this the correct formula (compare with LB)
            self.LayerResults[key].absorbedI =  self.LayerResults[key].alpha * self.LayerResults[key].Esquare # * self.LayerResults[key].n --> already applied
            self.LayerResults[key].absorption = integrate.trapz(self.LayerResults[key].absorbedI, x=x, axis=0) # 
            self.integrAbsorption[key] = integrate.trapz(self.LayerResults[key].absorption, x=wvl, axis=0)
            # fill dict with curves while sum up if sublayer is part of graded layer
            if self.LayerResults[key].criSource == 'graded':
                name = self.LayerResults[key].parentName
                if name not in absorptionCurves.keys():
                    absorptionCurves[name] = self.LayerResults[key].absorption
                else:
                    absorptionCurves[name] = absorptionCurves[name] + self.LayerResults[key].absorption
            else:
                absorptionCurves[key] = self.LayerResults[key].absorption
                
            self.absorbedIntensity.extend(integrate.trapz(self.LayerResults[key].absorbedI, x=self.wavelength, axis=1))
                
        # new loop because all values of integrAbsorption are required
        # calculate scalar values and sum up if layers are graded
        relAbsorption = {}
        absAbsorption = {}
        for i, key in enumerate(self.names):
            self.LayerResults[key].relAbsorption = self.integrAbsorption[key] / np.sum(list(self.integrAbsorption.values())) * self.scalars['absorbance (%)']/100
            #self.LayerResults[key].absAbsorption = self.LayerResults[key].relAbsorption * self.Jmax
            self.LayerResults[key].absAbsorption = integrate.trapz(self.LayerResults[key].absorption * self.spectrumCurrent, x=wvl, axis=0)
            
            if self.LayerResults[key].criSource == 'graded':
                name = self.LayerResults[key].parentName
                if name not in relAbsorption.keys():
                    relAbsorption[name] = self.LayerResults[key].relAbsorption * 100
                    absAbsorption[name] = self.LayerResults[key].absAbsorption
                else:
                    relAbsorption[name] = relAbsorption[name] + self.LayerResults[key].relAbsorption * 100
                    absAbsorption[name] = absAbsorption[name] + self.LayerResults[key].absAbsorption
            else:
                relAbsorption[key] = self.LayerResults[key].relAbsorption * 100
                absAbsorption[key] = self.LayerResults[key].absAbsorption     
                
        # take original stack without roughness layer
        for layer in self.layerstack.stack_rough:
            name = layer.name
            self.scalars['absorption layerwise (%) '].append(relAbsorption[name])
            self.scalars['absorption layerwise (mA/cm²) '].append(absAbsorption[name])
            
            self.addPlot({name : absorptionCurves[name]}, 'spectra', 'absorption (layerwise)')
        
        self.addPlot({'absorbed light' : self.absorbedIntensity}, 'profiles', 'E-field intensity')
        
        logging.info('\tcalculation of layerwise absorption finished.')
        
    def calcCollection(self):
        logging.info('\tcalculate layerwise collection...')
        integrCollection = {}
        collectedCurves = {}
        self.fc = []
        wvl = self.wavelength
        
        for key in self.names:
            x = self.LayerResults[key].x
            self.LayerResults[key].collectedI = self.LayerResults[key].absorbedI * self.LayerResults[key].fc[:, np.newaxis]
            self.LayerResults[key].collected = integrate.trapz(self.LayerResults[key].collectedI, x=x, axis=0) # 
            integrCollection[key] = integrate.trapz(self.LayerResults[key].collected, x=wvl, axis=0) 
            # fill dict with curves while sum up if sublayer is part of graded layer
            if self.LayerResults[key].criSource == 'graded':
                name = self.LayerResults[key].parentName
                if name not in collectedCurves.keys():
                    collectedCurves[name] = self.LayerResults[key].collected
                else:
                    collectedCurves[name] = collectedCurves[name] + self.LayerResults[key].collected
            else:
                collectedCurves[key] = self.LayerResults[key].collected
            # make full fc profile
            self.fc.extend(self.LayerResults[key].fc)
        
        # new loop because all values of integrAbsorption are required
        # calculate scalar values and sum up if layers are graded
        relCollection = {}
        absCollection = {}
        for i, key in enumerate(self.names):
            self.LayerResults[key].relCollection = integrCollection[key] / np.sum(list(self.integrAbsorption.values())) * self.scalars['absorbance (%)']/100
            #self.LayerResults[key].absCollection = self.LayerResults[key].relCollection * self.Jmax
            self.LayerResults[key].absCollection = integrate.trapz(self.LayerResults[key].collected * self.spectrumCurrent, x=wvl, axis=0) 
            if self.LayerResults[key].criSource == 'graded':
                name = self.LayerResults[key].parentName
                if name not in relCollection.keys():
                    relCollection[name] = self.LayerResults[key].relCollection * 100
                    absCollection[name] = self.LayerResults[key].absCollection
                else:
                    relCollection[name] = relCollection[name] + self.LayerResults[key].relCollection * 100
                    absCollection[name] = absCollection[name] + self.LayerResults[key].absCollection
            else:
                relCollection[key] = self.LayerResults[key].relCollection * 100
                absCollection[key] = self.LayerResults[key].absCollection
                
            # take original stack
        for layer in self.layerstack.stack_rough:
            name = layer.name
            self.scalars['collection layerwise (%) '].append(relCollection[name])
            self.scalars['collection layerwise (mA/cm²) '].append(absCollection[name])
            
            self.addPlot({name : collectedCurves[name]}, 'spectra', 'collection (layerwise)')
        
        self.addPlot({'complete stack': self.fc}, 'profiles', 'collection function')
        logging.info('\tcalculation of layerwise collection finished.')
        
    def calcQE(self):
        self.calcCollection()
        logging.info('\tcalculate quantum efficiency...')
        self.EQE = np.zeros(len(self.wavelength))
        for name in self.names:
            # sum up collection of all layers
            self.EQE = self.EQE + np.abs(self.LayerResults[name].collected)
        self.addPlot({'EQE': self.EQE}, 'spectra', 'QE')
        self.addPlot({'IQE': self.EQE/np.abs(self.AspectrumSystem)}, 'spectra', 'QE')
        
         # calc deviation from reference
        if 'EQE reference' in self.references:
         #   costFunc1EQE = np.sum(((self.EQE_reference-self.EQE))**2)
          #  costFunc2EQE = np.sum((self.EQE*(self.EQE_reference-self.EQE))**2) 
            costFunc3EQE = np.sum(((self.EQE - self.EQE_reference)/self.EQE_reference)**2)
        
           # self.scalars['costFunc1EQE'] = costFunc1EQE 
            self.scalars['Chi Square EQE'] = costFunc3EQE 
        
        logging.info('\tcalculation of quantum efficiency finished.')
        
    def calcGeneration(self):
        '''
        calculated generation rate per
        - wavelength:   G_wl 
        - location:     G_x
        - both:         G_wl_x
        
        Q = spectrum * I = n*alpha*abs(E²*E0²) = I0 * I * alpha * n = 1/2*c*e0*alpha*abs(E²)
        G = Q * lambda/h*c
        
        '''
        logging.info('\tcalculate generation profile...')
        h = 6.62606957e-34 # Js Planck's constant
        c = 2.99792458e8 #m/s speed of light
        q = 1.602176e-19 #C electric chargeq 
    
        wvl = self.wavelength

        for key in self.names:
            #Energy dissipation W/m²-nm-nm at each position and wavelength (JAP Vol    % 86 p.487 Eq 22)
            self.LayerResults[key].Q = self.spectrum * self.LayerResults[key].absorbedI
            # generation rate per second-cm²-nm-nm at each position and wavelength
            self.LayerResults[key].G_wl_x = self.LayerResults[key].Q * self.wavelength * 1e-13 / (h * c)
            # Exciton generation rate as a function of position/(sec-cm^2-nm)
            self.LayerResults[key].G_x = integrate.trapz(self.LayerResults[key].G_wl_x, x=wvl, axis = 1)
            
            # how much is oollected
            self.LayerResults[key].el_G_wl_x = self.spectrum * self.LayerResults[key].collectedI * self.wavelength * 1e-13 / (h * c)
            self.LayerResults[key].el_G_x = integrate.trapz(self.LayerResults[key].el_G_wl_x, x=wvl, axis = 1)
        
        #self.G_x = np.zeros((len(self.wavelength), 1))
        self.G_wl_x = []
        self.el_G_wl_x = []
        self.G_x = []
        self.el_G_x = []
        
        for i, key in enumerate(self.names):
            self.G_wl_x.extend(self.LayerResults[key].G_wl_x * 1e7) # 1/cm^2-s-nm-nm --> 1/cm^3-s-nm
            self.el_G_wl_x.extend(self.LayerResults[key].el_G_wl_x * 1e7) # 1/cm^2-s-nm-nm --> 1/cm^3-s-nm
            self.G_x.extend(self.LayerResults[key].G_x * 1e7) # 1/cm^2-s-nm --> 1/cm^3-s
            self.el_G_x.extend(self.LayerResults[key].el_G_x * 1e7) # 1/cm^2-s-nm --> 1/cm^3-s
        
        self.addPlot({'electrical collection' : np.array(self.G_wl_x)}, '2D')
        self.addPlot({'optical generation' : np.array(self.el_G_wl_x)}, '2D')
        self.addPlot({'optical generation (1/cm³s)': self.G_x}, 'profiles', 'generation')
        self.addPlot({'electrical collection (1/cm³s)': self.el_G_x}, 'profiles', 'generation')
        
        # calc current G * q [1/cm^2-nm-s * As]
        self.generatedCurrent = integrate.trapz(self.el_G_x, x=self.x, axis = 0) * q * 1000 / 1e7
        self.scalars['generated current (mA/cm²)'] = self.generatedCurrent
        logging.info('\tcalculation of generation profile finished.')
        
    def calcOptBeamTotal(self):
        logging.info('\tcalculate Lambert-Beer optics...')
        h = 6.62606957e-34 # Js Planck's constant
        c = 2.99792458e8 #m/s speed of light
        wvl = self.wavelength
        
        I = np.ones(len(wvl))
        self.I_LB = []
        self.I_LB_x = []
        integrAbsorption = {}
        integrCollection = {}
        self.LB_el_G_wl_x = []
        self.LB_el_G_x = []
        A = np.zeros(len(wvl))
        self.EQE_LB = np.zeros(len(wvl))
        
        if self.calculationOptions['LBcorrection'] and self.references['R reference'][0]:
            I = I * (1 - self.R_reference)

        for key in self.names:
            alpha = self.LayerResults[key].alpha
            x = self.LayerResults[key].x
            EXP = x[:, np.newaxis]
            Ivector = I*np.exp(-alpha*EXP)
            I_end = Ivector[-1]
            
            self.LayerResults[key].absorbedILB = self.LayerResults[key].alpha * Ivector #self.LayerResults[key].n
            self.LayerResults[key].absorptionLB = integrate.trapz(self.LayerResults[key].absorbedILB, x=x, axis=0) # 
            self.LayerResults[key].collectedILB = self.LayerResults[key].absorbedILB * self.LayerResults[key].fc[:, np.newaxis]
            self.LayerResults[key].collectedLB = integrate.trapz(self.LayerResults[key].collectedILB, x=x, axis=0) # 
            
            # for scalars
            integrAbsorption[key] = integrate.trapz(self.LayerResults[key].absorptionLB, x=wvl, axis=0)
            integrCollection[key] = integrate.trapz(self.LayerResults[key].collectedLB, x=wvl, axis=0) 
            
            # total absorption/ collection
            A = A + self.LayerResults[key].absorptionLB
            self.EQE_LB = self.EQE_LB + self.LayerResults[key].collectedLB
            
            self.I_LB.extend(Ivector)
            self.I_LB_x.extend((integrate.trapz(Ivector, x=wvl, axis = 1) / (wvl[-1] - wvl[0])))
            # how much is oollected
            LB_el_G_wl_x = self.spectrum * self.LayerResults[key].collectedILB * wvl * 1e-13 / (h * c)
            LB_el_G_x = integrate.trapz(LB_el_G_wl_x, x=wvl, axis = 1)
            self.LB_el_G_wl_x.extend(LB_el_G_wl_x * 1e7)
            self.LB_el_G_x.extend(LB_el_G_x * 1e7)
            
            # go to next layer
            I = I_end
            # end this loop
        
        # total absorption scalars
        lengthWvl = self.wavelength[-1] - self.wavelength[0]
        AnumLB = integrate.trapz(A, x = wvl, axis=0) / lengthWvl    #len(wvl)
        self.scalars['absorbance LB (%)'] = AnumLB * 100 #'%.4f' % 
        #self.scalars['absorbance LB (mA/cm²)'] = AnumLB * self.Jmax
        self.scalars['absorbance LB (mA/cm²)'] = integrate.trapz(A * self.spectrumCurrent, x = wvl, axis=0)
        
        # new loop because all values of integrAbsorption/collection are required
        # calculate scalar values and sum up if layers are graded
        absorptionCurves = {}
        collectedCurves = {}
        relAbsorption = {}
        absAbsorption = {}
        relCollection = {}
        absCollection = {}
        for key in self.names:    
            self.LayerResults[key].relAbsorptionLB = integrAbsorption[key] / np.sum(list(integrAbsorption.values())) * self.scalars['absorbance LB (%)']/100
            #self.LayerResults[key].absAbsorptionLB = self.LayerResults[key].relAbsorptionLB * self.Jmax
            self.LayerResults[key].absAbsorptionLB = integrate.trapz(self.LayerResults[key].absorptionLB * self.spectrumCurrent, x = wvl, axis=0)
            self.LayerResults[key].relCollectionLB = integrCollection[key] / np.sum(list(integrAbsorption.values())) * self.scalars['absorbance LB (%)']/100
            #self.LayerResults[key].absCollectionLB = self.LayerResults[key].relCollectionLB * self.Jmax
            self.LayerResults[key].absCollectionLB = integrate.trapz(self.LayerResults[key].collectedLB * self.spectrumCurrent, x = wvl, axis=0)
            # fill dicts with curves while sum up if sublayer is part of graded layer
            if self.LayerResults[key].criSource == 'graded':
                name = self.LayerResults[key].parentName
                if name not in absorptionCurves.keys():
                    absorptionCurves[name] = self.LayerResults[key].absorptionLB
                    collectedCurves[name] = self.LayerResults[key].collectedLB
                    relAbsorption[name] = self.LayerResults[key].relAbsorptionLB * 100
                    absAbsorption[name] = self.LayerResults[key].absAbsorptionLB
                    relCollection[name] = self.LayerResults[key].relCollectionLB * 100
                    absCollection[name] = self.LayerResults[key].absCollectionLB
                else:
                    absorptionCurves[name] = absorptionCurves[name] + self.LayerResults[key].absorptionLB
                    collectedCurves[name] = collectedCurves[name] + self.LayerResults[key].collectedLB
                    relAbsorption[name] = relAbsorption[name] + self.LayerResults[key].relAbsorptionLB * 100
                    absAbsorption[name] = absAbsorption[name] + self.LayerResults[key].absAbsorptionLB
                    relCollection[name] = relCollection[name] + self.LayerResults[key].relCollectionLB * 100
                    absCollection[name] = absCollection[name] + self.LayerResults[key].absCollectionLB
            else:
                absorptionCurves[key] = self.LayerResults[key].absorptionLB
                collectedCurves[key] = self.LayerResults[key].collectedLB
                relAbsorption[key] = self.LayerResults[key].relAbsorptionLB * 100
                absAbsorption[key] = self.LayerResults[key].absAbsorptionLB
                relCollection[key] = self.LayerResults[key].relCollectionLB * 100
                absCollection[key] = self.LayerResults[key].absCollectionLB
            
        # take original stack and create layerwise plots
        for layer in self.layerstack.stack_rough:
            name = layer.name
            self.scalars['absorption layerwise LB (%) '].append(relAbsorption[name])
            self.scalars['absorption layerwise LB (mA/cm²) '].append(absAbsorption[name])
            self.scalars['collection layerwise LB (%) '].append(relCollection[name])
            self.scalars['collection layerwise LB (mA/cm²) '].append(absCollection[name])
            self.addPlot({'{} LB'.format(name) : absorptionCurves[name]}, 'spectra', 'absorption (layerwise)')
            self.addPlot({'{} LB'.format(name) : collectedCurves[name]}, 'spectra', 'collection (layerwise)')
        
        self.addPlot({'absorption LB' : A})
        self.addPlot({'light intensity': self.I_LB_x}, 'profiles', 'light intensity LB')
        self.addPlot({'light intensity LB' : np.array(self.I_LB)}, '2D')
        self.addPlot({'el. generation LB' : np.array(self.LB_el_G_wl_x)}, '2D')
        self.addPlot({'electrical generation LB  (1/cm³s)': self.LB_el_G_x}, 'profiles', 'generation')
        self.addPlot({'EQE LB': self.EQE_LB}, 'spectra', 'QE')
        logging.info('\tcalculation of Lambert-Beer optics finished.')

        
