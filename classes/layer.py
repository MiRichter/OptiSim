'''
class for creating a layer object
'''
from PyQt5.QtGui import QColor
import numpy as np
import numexpr as ne

class Layer:
    '''
    class of type Layer with properties 'name', 'thickness', 'nk'
    '''
    def __init__(self, name,
                thickness=100, 
                criSource='constant',  
                criDBName = 'Si', 
                criFile = {'path': '', 'alpha': False, 'n': 2.0}, 
                criConstant = [1.0, 0.0]):
        '''
        criSource:
        0 -- from MaterialDB
        1 -- from specified File
        3 -- constant
        '''
        #self.parent = MainWindow
        self.name = name
        self.parentName = name
        self.thickness = thickness
        self.thick = False
        self.criSource = criSource
        self.criFile = criFile.copy()
        self.criDBName = criDBName
        self.criConstant = criConstant
        self.criGrading = { 'mode': 'constant', 
                            'value': 0.0, 
                            'files': [[0, 1, self.criFile['path']], [1, 2, self.criFile['path']]], 
                            'xMoles': [],
                            'Egs': [], 
                            'n_idc': [], 
                            'k_idc': []}
                            
        self.dielectricFunction = { 'e0': 0.0, 
                                    'oscillators': [{'name': 'Lorentz', 'values': [1, 3, 0.2], 'active': True}], 
                                    'spectral range': [0.5, 4.0], 
                                    'n': [], 
                                    'k': [], 
                                    'wvl': []
                                    }
                                    
                            
                            
        self.mesh = {   'meshing': 0, 
                        'Points': 100, 
                        'Dist':  1, 
                        'refine': False
                       }
        
        self.color = QColor(255, 255, 255)
        self.srough = False
        self.sroughThickness = 0
        self.sroughHazeR = 0.0
        self.sroughHazeT = 0.0
        
        self.x = None
        self.wavelength = None
        self.n = None
        self.k = None
        
        self.collection = {'source': 'from collection function', 
                            'mode': 'constant', 'value': 1.0, 
                            'SCRwidth': 300, 'diffLength': 1000, 'recVel': 1e7, 'SCRside': 0} # default
        
        self.makeXnodes()
        self.makeXcollection()
        self.makeXgrading()
        
        
    def makeXnodes(self):
        mode = self.mesh['meshing']
        number = self.mesh['Points']
        step = self.mesh['Dist']
        if mode == 2: #'optimized':
            self.x = [0]
            x = 1
            while x < self.thickness/2:
                self.x.append(x)
                x *= 1.1
            self.x2 = [self.thickness-i for i in self.x]
            self.x.extend(self.x2[::-1])
        elif mode == 1: # 'constant distance':
            self.x = np.arange(0, self.thickness, step)
        else: #'fixed number'
            self.x = np.linspace(0, self.thickness, number)
            
        self.x = np.array(self.x)
            
    def makeXcollection(self):
        if self.collection['source'] == 'from collection function':
            if self.collection['mode'] == 'constant':
                fc = np.ones(len(self.x)) * self.collection['value']
            elif self.collection['mode'] == 'linear':
                fc = -((self.collection['value'][0] - self.collection['value'][1]) * self.x / self.thickness) \
                            + self.collection['value'][0]
            elif self.collection['mode'] == 'function':
                x = self.x
                dx = self.thickness
                fc = ne.evaluate(self.collection['value'])
            fc[fc > 1] = 1.0
            fc[fc < 0] = 0.0
            self.fc = np.array(fc)
        else: # from diffusion length for constant difflength and constant field ((GreenProg. Photovolt: Res. Appl. 2009; 17:57–66, Eq. (22)
            fc = np.zeros(len(self.x))
            W_scr = self.collection['SCRwidth']
            L = self.collection['diffLength']
            if 'grading' in self.collection:
                beta = self.collection['grading']
            else:
                beta = 0.0
                
            x = self.x
            #x2 = self.x[self.x >= w] - w
            W_abs = self.thickness
            S = self.collection['recVel']                    # [cm/s] Oberflächenrekombination
            D = 1.55                  # [cm²/s] Diffusionskonstante (also 1cm^2/s)
            #beta = 89                   # [meV/µm] d(Bandlückenänderung)/dx; aus Thorstens MA
            kB = 8.617e-5;            # [eV/K] Boltzmann
            T = 300               # [K] Temperatur
            chi = 1e-6*beta/(kB*T)   # [1/nm] reduziertes Feld
            L_ = L/np.sqrt(1+(chi*L/2)**2) # [nm]
            S_ = S + chi*D*1e7/2      # [cm/s]
            
            
            if self.collection['SCRside'] == 1: # bottom
                fc[self.x[::-1] <= W_scr] = 1
            else: # top
                #fc[self.x < w] = 1
                #fc[self.x >= w] = np.exp(-x2/2)*np.cosh(x2/L)/np.cosh(w/L)
                # nach Green Prog. Photovolt: Res. Appl. 2009; 17:57–66;  Eq. (22)
                fc = np.exp(chi*(x-W_scr)/2) * (np.cosh((W_abs-(x-W_scr))/L_) + 1e-7*S_*L_/D*np.sinh((W_abs-(x-W_scr))/L_)) / (np.cosh(W_abs/L_) + 1e-7*(S_*L_/D)*np.sinh(W_abs/L_))
                
                
            fc[fc > 1] = 1.0
            fc[fc < 0] = 0.0
            self.fc = fc
            
    def makeXgrading(self):
        if self.criGrading['mode'] == 'constant':
            self.xMole = np.ones(len(self.x)) * self.criGrading['value']
        elif self.criGrading['mode'] == 'linear':
            self.xMole = -((self.criGrading['value'][0] - self.criGrading['value'][1]) * self.x / self.thickness) \
                        + self.criGrading['value'][0]
        elif self.criGrading['mode'] == 'function':
            x = self.x
            dx = self.thickness
            self.xMole = ne.evaluate(self.criGrading['value'])
        self.xMole[self.xMole > 1] = 1.0
        self.xMole[self.xMole < 0] = 0.0
