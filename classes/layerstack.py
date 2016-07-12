'''
Class for stack of layers as used for calculation
'''
from classes.layer import Layer

import time
import logging
import copy
import numpy as np
import scipy as sp
from classes.errors import *
from numpy import cos #, inf, zeros, array, exp, conj, nan, isnan
from scipy.interpolate import interp1d

def snell(cri1, cri2, theta1):
    '''
    calculates the (complex) angle per wavelength of the light propagation by Snell's law
    '''
    return sp.arcsin(np.real_if_close(cri1*np.sin(theta1) / cri2))
    
    
class LayerStack:
    def __init__(self, stackname, stack, settings, getCRICallback):
        '''
        input:
        stack class with
        name
        thickness
        cri source
        cri file / constant
        grading ??
        wavelength range
        
        output:
        modified layerstack including layer matrices
        
        '''
        logging.info('\nstart creating final stack...')
        layers = []
        for i in stack:
            layers.append('\t\t' + '\t\t'.join([i.name, str(i.thickness) + ' nm']))
        logging.info('\toriginal stack with Name {} consists of {} layers:\n'.format(stackname, len(layers)) + '\n'.join(layers))
        
        self.stack = copy.deepcopy(stack)
        self.stackname = stackname
        startCreationTime = time.time()
        self.wavelength = settings['wavelength']
        wvl = np.array(self.wavelength)
        eV = 1239.941 / wvl
        self.theta0 = settings['angle'] * np.pi/180 # angle of incident in radians
        self.intensity = settings['intensity'] / 100 # factor used in optics class
        self.layersequence = copy.deepcopy(stack) # change if TMM stack not actual Stack (Grading, Roughness)
        self.stack_rough = self.stack.copy()
        
        #TODO: check if layers have the same name
        self.HazeOn = False # Flag for calculating diffused light
        i = 0
        self.gradedLayers = []
        noOfGradedLayers = 0
        currentPosition = 0
        currentRoughPosition = 0
        # create complete layerstack (add roughness and graded layers)
        while i < len(stack):
            layer = stack[i]
            if layer.srough == True and layer.sroughThickness > 0 and settings['roughness EMA model']:
                logging.info('\tadd interface roughness layer on top of {}...'.format(layer.name))
                notRoughFlag = False
                sroughLayer = Layer(layer.name + '_rough')
                sroughLayer.parentName = layer.name
                sroughLayer.thickness = layer.sroughThickness
                #sroughLayer.thick = layer.thick
                sroughLayer.collection = layer.collection
                sroughLayer.srough = True
                sroughLayer.sroughHazeR = layer.sroughHazeR
                sroughLayer.sroughHazeT = layer.sroughHazeT
                #layer.sroughHaze = 0
                sroughLayer.makeXnodes()
                sroughLayer.makeXcollection()
                self.layersequence.insert(currentPosition, sroughLayer)
                self.stack_rough.insert(currentRoughPosition, sroughLayer)
                # set surface roughness of original layer to zero
                self.layersequence[i+1].sroughHazeR = 0.0
                self.layersequence[i+1].sroughHazeT = 0.0
                i += 1
                currentPosition += 2
                currentRoughPosition += 2
            else:
                notRoughFlag = True
            if layer.criSource == 'graded':
                notGradedFlag = False
                name = layer.name
                self.gradedLayers.append([])
                if notRoughFlag:
                    currentPosition = currentPosition
                else:
                    currentPosition = currentPosition - 1
                self.layersequence.pop(currentPosition)
                getCRICallback(layer)
                step = 5 # TODO: number of Xnodes which contain one graded layer (setting)
                logging.info('\treplace layer {} with one graded layer for each {} meshpoints and assign collection and xMole...'.format(name, step))
                idxrange = range(0, len(layer.x), step)
                for no, idx in enumerate(idxrange):
                    gradedLayer = Layer(layer.name + '_graded' + str(no))
                    gradedLayer.parentName = name
                    gradedLayer.criSource = 'graded'
                    gradedLayer.x = layer.x[idx:idx+step+1] - layer.x[idx]
                    gradedLayer.thickness = gradedLayer.x[-1]
                    gradedLayer.fc = layer.fc[idx:idx+step+1]
                    gradedLayer.xMole = layer.xMole[idx] # only top of layer is considered
                    gradedLayer.wavelength = layer.wavelength
                    gradedLayer.criGrading = layer.criGrading
                    gradedLayer.thick = layer.thick
                    self.gradedLayers[noOfGradedLayers].append(currentPosition)
                    self.layersequence.insert(currentPosition, gradedLayer)
                    currentPosition += 1
                i += 1
                noOfGradedLayers += 1
            else:
                notGradedFlag = True
            if notRoughFlag and notGradedFlag:
                i += 1
                currentPosition += 1
        
    
        self.names = []
        self.thicknesses = []
        roughLayers = []
        self.getCRI = getCRICallback
        
        #TODO: Check Input
        
        # get cri for normal layers
        for i, element in enumerate(self.layersequence):
            self.names.append(element.name)
            self.thicknesses.append(element.thickness)
            # load all cri except graded
            if '_graded' in element.name:
                continue   # created in next for statement
            self.getCRI(element)
            if element.criSource == 'constant':
                pass    # already maked
            if '_rough' in element.name:
                roughLayers.append(i)
                continue   # created in next for statement
            else:
                element.n = np.interp(wvl, element.wavelength, element.n)
                element.k = np.interp(wvl, element.wavelength, element.k)
                
        #get cri for graded layers
        for i, layerParent in enumerate(self.gradedLayers):
            for index in self.gradedLayers[i]:
                layer = self.layersequence[index]
                xMoles = np.array(layer.criGrading['xMoles'])
                Egs = np.array(layer.criGrading['Egs'])
                n_idx = np.array(layer.criGrading['n_idc']).T
                k_idx = np.array(layer.criGrading['k_idc']).T
                if layer.xMole in xMoles:
                    idx = np.nonzero(xMoles == layer.xMole)
                    layer.n = np.reshape(n_idx[:, idx], len(wvl))
                    layer.k = np.reshape(k_idx[:, idx], len(wvl))
                    continue
                if settings['grading advanced']:
                    # this method takes the two adjacent nk-files matching the required xMole
                    # and moves the curves according to the given Eg
                    idx1 = np.nonzero(xMoles < layer.xMole)
                    idx2 = np.nonzero(xMoles > layer.xMole)
                    idx1 = idx1[0][-1]
                    idx2 = idx2[0][0]
                    Eg1 = Egs[idx1]
                    Eg2 = Egs[idx2]
                    n1 = n_idx[:, idx1].T
                    n2 = n_idx[:, idx2].T
                    k1 = k_idx[:, idx1].T
                    k2 = k_idx[:, idx2].T
                    eV1 = eV + (Eg2 - Eg1) * layer.xMole
                    #eV2 = eV - (Eg2 - Eg1) * layer.xMole
                    n1 = interp1d(eV1,n1, bounds_error=False)(eV)
                    n2 = interp1d(eV1,n2, bounds_error=False)(eV)
                    k1 = interp1d(eV1,k1, bounds_error=False)(eV)
                    k2 = interp1d(eV1,k2, bounds_error=False)(eV)
                    for k in range(len(wvl)):
                        if np.isnan(n1[k]):
                            if np.isnan(n1[k-1]):
                                n1[k] = n1[k+1]
                                n2[k] = n2[k+1]
                                k1[k] = 0
                                k2[k] = 0
                            else:
                                n1[k] = n1[k-1]
                                n2[k] = n2[k-1]
                                k1[k] = 0
                                k2[k] = 0
                    #n1 = np.nan_to_num(n1)
                    #n2 = np.nan_to_num(n2)
                    #k1 = np.nan_to_num(k1)
                    #k2 = np.nan_to_num(k2)
                    layer.n = np.reshape(np.mean(np.array([n1, n2]), axis=0), len(wvl)).T
                    layer.k = np.reshape(np.mean(np.array([k1, k2]), axis=0), len(wvl)).T
                    #print(layer.k)
                else:
                    n = []
                    k = []
                    for i in range(len(wvl)):
                        n.append(np.interp(layer.xMole, xMoles, n_idx[i]))
                        k.append(np.interp(layer.xMole, xMoles, k_idx[i]))
                    layer.n = np.array(n)
                    layer.k = np.array(k)
                
        #get cri for roughness layers
        for index in roughLayers:
            if index == 0:
                prev_n = np.ones(len(wvl))
                prev_k = np.zeros(len(wvl))
            else:
                prev_n = self.layersequence[index - 1].n
                prev_k = self.layersequence[index - 1].k
            if index == len(self.layersequence):
                next_n = np.ones(len(wvl))
                next_k = np.zeos(len(wvl))
            else:
                next_n = self.layersequence[index + 1].n
                next_k = self.layersequence[index + 1].k
                
            layer = self.layersequence[index]
            '''
            Maxwell-Garnett (f_B is ratio , e.g. 0.5):
            e - e_A        e_B - e_A
            ________ = f_B __________ 
            e + 2e_A       e_B + 2e_A
            
                        2 f_B * (e_B - e_A) + e_B + 2 e_A
            --> e = e_A _________________________________      (Wikipedia)
                           2e_A + e_B + f_B (e_A - e_B)
            
            
            Bruggemann (f_A = 1-f_B is ratio , e.g. 0.5):
                e_A - e        e_B - e
            f_A ________ + f_B __________ = 0
                e_A + 2e       e_B + 2e
            
            
            -->  e = b +/- (b + (e_A*e_B)/2 ) ^0.5
            
                        (3f_B - 1) (e_B- e_A) + e_A
                    b = ____________________________
                                    4
            
            Mean:
            
            n = 0.5 (n_A + n_B)
            k = 0.5 (k_A + k_B)
            
            '''
            if 'EMA model' in settings:
                EMAmodel = settings['EMA model']
            else:
                EMAmodel = 0 # old versions (< 0.5.0)
            
            if EMAmodel == 0: # Mean
                layer.n = (prev_n + next_n) / 2
                layer.k = (prev_k + next_k) / 2
            else:
                e_A =  (prev_n**2 - prev_k**2) + 1j * 2*prev_n*prev_k
                e_B =  (next_n**2 - next_k**2) + 1j * 2*next_n*next_k
                
                if EMAmodel == 1: # Bruggemann
                    b = ((3 * 0.5 - 1) * (e_B - e_A) + e_A) / 4.0
                    e = b + (b + (e_A * e_B) / 2 )**0.5
                else: # Maxwell-Garnett
                    e = e_A * (2 * 0.5 * (e_B - e_A) + e_B + 2 * e_A) / (2 * e_A + e_B + 0.5 * (e_A - e_B))
                
                e1 = np.real(e)
                e2 = np.imag(e)
                layer.n = (0.5 * (e1 + (e1**2 + e2**2)**0.5))**0.5
                layer.k = (0.5 * (-e1 + (e1**2 + e2**2)**0.5))**0.5
            
        
        # make complex refractive index and layer matrices
        for i, layer in enumerate(self.layersequence):
            layer.cri = layer.n + 1j * layer.k
            layer.alpha = 4*np.pi*layer.k/wvl #*1e-7
            # make angle of lightwave in each layer
            if i == 0:
                cri1 = np.ones((len(wvl)), np.complex)
                layer.theta = snell(cri1, layer.cri, self.theta0)
            else:
                layer.theta = snell(self.layersequence[i-1].cri, layer.cri, self.layersequence[i-1].theta)
            #TODO: what about the last interface?
            layer.xi = 2 * np.pi * layer.cri * cos(layer.theta) / wvl
            # layer matrix according to Egn 6 Pettersson
            layer.LayerMatrix = np.zeros((len(wvl), 2, 2), np.complex)
            layer.LayerMatrixInc = np.zeros((len(wvl), 2, 2), np.complex)
            
            EXP = 1j * layer.xi * layer.thickness
            
            #if layer.thick:
             #   EXP = EXP * 1000 # convert from mum to mm
            # calculate electric field propagation matrix
            layer.LayerMatrix[:, 0, 0] = np.exp(-EXP)
            layer.LayerMatrix[:, 1, 1] = np.exp(EXP)
            # calculate intensity propagation matrix
            layer.LayerMatrixInc[:, 0, 0] = np.abs(np.exp(-EXP))**2
            layer.LayerMatrixInc[:, 1, 1] = np.abs(np.exp(EXP))**2
            
            if layer.sroughHazeR > 0 or layer.sroughHazeT > 0 or self.HazeOn:
                if layer.srough and settings['roughness Haze calc diffuse'][0]:
                    self.HazeOn = True
                 
        self.creationTime = time.time() - startCreationTime
        layers = []
        for i in self.layersequence:
            layers.append('\t\t' + '\t\t'.join([i.name, str(i.thickness) + ' nm'])) #, str(np.max(i.n)), str(np.min(i.n)), str(np.max(i.k)), str(np.min(i.k))
            # write all nk data to files
            fname = 'tmp_nk_{}.txt'.format(i.name)
            try:
                f = open(fname, 'w')
                for idx, wvl in enumerate(self.wavelength):
                    f.write('{}\t{}\t{}\n'.format(wvl, i.n[idx], i.k[idx]))
                f.close()
            except IOError as e:
                raise WriteError("Could not write data to file {}: \n {}".format(fname, e.args[1]))
        
        logging.info('\tfinal stack created:\n' + '\n'.join(layers))
        logging.info('... final stack creation time {:.3f}'.format(self.creationTime))
        
        
        #print(self.names)


        
