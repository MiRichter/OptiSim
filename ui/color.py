# -*- coding: utf-8 -*-

"""
Module implementing ColorDlg.
"""

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog

from .Ui_color import Ui_Dialog

import colorpy, colorpy.illuminants, colorpy.colormodels
import numpy as np


class ColorDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, results, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super(ColorDlg, self).__init__(parent)
        self.setupUi(self)
        
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.results = results
        listOfResults = []
        for result in results:
            if 'reflection' in result.availablePlots['spectra']['total A,R,T']:
                listOfResults.append(result.stackname)
                
        self.resultsCB.addItems(listOfResults)
        #self.resultsCB.setCurrentIndex(0)
        self.currentResult = self.results[0]
        
        self.illuminant = 0 # 0 - D65; 1 - illuminant A; 2 - bb with T; 3 - constants
        self.source = 0 # reflection, else transmission
        self.temp = 3000
        
        self.wvl = np.arange(360, 831) # default resolution for colorpy ciexyz
        num_wl = len(self.wvl)
        # get rgb colors for each wavelength
        self.rgb_colors =  np.empty ((num_wl, 3))
        for i in range (0, num_wl):
            wl_nm = self.wvl[i]
            xyz = colorpy.ciexyz.xyz_from_wavelength (wl_nm)
            self.rgb_colors[i] = colorpy.colormodels.rgb_from_xyz (xyz)
        # scale to make brightest rgb value = 1.0
        rgb_max = np.max (self.rgb_colors)
        scaling = 1.0 / rgb_max
        self.rgb_colors *= scaling  
        
        if listOfResults:
            self.calcColor()
        
    def calcColor(self):
            
        if self.illuminant == 0: 
            illuminant = colorpy.illuminants.get_illuminant_D65()
        elif self.illuminant == 1:
            illuminant = colorpy.illuminants.get_illuminant_A()
        elif self.illuminant == 2:
            illuminant = colorpy.illuminants.get_blackbody_illuminant(self.temp)
        else:
            illuminant = colorpy.illuminants.get_constant_illuminant()
            
        illuminant = np.array(illuminant)
        
        if self.source == 0:
            spectrum = self.currentResult.availablePlots['spectra']['total A,R,T']['reflection']
        else:
            spectrum = self.currentResult.availablePlots['spectra']['total A,R,T']['transmission']
        
        spectrum = np.interp(self.wvl, self.currentResult.wavelength, spectrum)

        IllumSpectrum = illuminant.copy()
        IllumSpectrum[:, 1] = spectrum * illuminant[:, 1]
 
        XYZ = colorpy.ciexyz.xyz_from_spectrum(IllumSpectrum)
    
        X,Y,Z = XYZ
        if Y > 1:
            print('Warning: Oversaturated color! XYZ = {}'.format(XYZ))
            
        xy = [X / (X + Y + Z), Y / (X + Y + Z)]
        xyY = [xy[0], xy[1], Y]
        rgb = colorpy.colormodels.rgb_from_xyz(XYZ)
        irgb = colorpy.colormodels.irgb_from_rgb(rgb)
        Lab = colorpy.colormodels.lab_from_xyz(XYZ)
        luv = colorpy.colormodels.luv_from_xyz(XYZ)
        
        colorString = colorpy.colormodels.irgb_string_from_irgb (irgb)
        self.colorFrame.setStyleSheet('background: {}'.format(colorString))
        self.colorSpecsTE.setText('color of {}:\nX, Y, Z: {:.3f}, {:.3f}, {:.3f}\nxy: {:.3f}, {:.3f}\nxyY: {:.3f}, {:.3f}, {:.3f}\nrgb: {:.3f}, {:.3f}, {:.3f}\nirgb: {}, {}, {}\nLab: {:.3f}, {:.3f}, {:.3f}\nluv: {:.3f}, {:.3f}, {:.3f}'.format(self.currentResult.stackname, 
                                                    X, Y, Z, 
                                                    xy[0], xy[1], 
                                                    xyY[0], xyY[1], xyY[2], 
                                                    rgb[0], rgb[1], rgb[2], 
                                                    irgb[0], irgb[1], irgb[2], 
                                                    Lab[0], Lab[1], Lab[2],
                                                    luv[0], luv[1], luv[2],))
                                                    
                                                    
        self.spectrumPlot.canvas.ax.clear() 
        self.spectrumPlot.canvas.ax.plot (IllumSpectrum [:,0], IllumSpectrum [:,1], color='k', linewidth=2.0, antialiased=True)
        self.spectrumPlot.canvas.ax.set_xlabel('wavelength (nm)')
        self.spectrumPlot.canvas.ax.set_ylabel('intensity ($W/m^2$)')
        
         # draw color patches (thin vertical lines matching the spectrum curve) in color
        for i in range (0, len(self.wvl)-1):    # skipping the last one here to stay in range
            x0 = IllumSpectrum [i][0]
            x1 = IllumSpectrum [i+1][0]
            y0 = IllumSpectrum [i][1]
            y1 = IllumSpectrum [i+1][1]
            poly_x = [x0,  x1,  x1, x0]
            poly_y = [0.0, 0.0, y1, y0]
            color_string = colorpy.colormodels.irgb_string_from_rgb (self.rgb_colors [i])
            self.spectrumPlot.canvas.ax.fill_between (poly_x, poly_y, facecolor=color_string, edgecolor=color_string)
        
        self.spectrumPlot.canvas.draw()
               
        """
    Calculate the color in various representations.
    
    spectrum is the output of calc_spectrum.
    
    scale is the scaling method. Possibilities are:

    * scale=None means don't scale. This is usually what you want, bucause
      the illuminant should be pre-scaled in an appropriate way.
      (Specifically, it's scaled to get Y=1 for a perfect reflector.)
    * scale='Y1' means that the intensity is increased or decreased in
      order to set Y (the luminance) to 1. So you can get white but not gray,
      you can get orange but not brown, etc.
    * scale=0.789 multiplies X,Y,Z by 0.789. Any number > 0 is OK.
    
    Returns a dictionary with rgb, irgb, xy, xyY, and XYZ. Definitions:

    * xy, xyY and XYZ are defined as in
        http://en.wikipedia.org/wiki/CIE_1931_color_space
    * rgb is the linear (i.e., proportional to intensity, not
      gamma-corrected) version of sRGB.
    * irgb is ready-to-display sRGB, i.e. it is clipped to the range 0-1,
      and gamma-corrected, and rounded to three integers in the range 0-255.

    (sRGB is the standard RGB used in modern displays and printers.)
    if scale == 'Y1' or type(scale) is float:
        factor = (1.0 / XYZ[1] if scale == 'Y1' else scale)
        XYZ[0] *= factor
        XYZ[1] *= factor
        XYZ[2] *= factor
    """
    
    @pyqtSlot(int)
    def on_resultsCB_activated(self, index):
        self.currentResult = self.results[index]
        self.calcColor()
    
    @pyqtSlot(bool)
    def on_sourceReflection_toggled(self, checked):
        if checked:
            self.source = 0
            self.calcColor()
    
    @pyqtSlot(bool)
    def on_sourceTransmission_toggled(self, checked):
        if checked:
            self.source = 1
            self.calcColor()
    
    @pyqtSlot(bool)
    def on_illD65_RB_toggled(self, checked):
        if checked:
            self.illuminant = 0
            self.calcColor()
    
    @pyqtSlot(bool)
    def on_illA_RB_toggled(self, checked):
        if checked:
            self.illuminant = 1
            self.calcColor()
    
    @pyqtSlot(bool)
    def on_illBB_RB_toggled(self, checked):
        if checked:
            self.illuminant = 2
            self.calcColor()
      
    @pyqtSlot(bool)
    def on_illConst_RB_toggled(self, checked):
        if checked:
            self.illuminant = 3
            self.calcColor()
    
    @pyqtSlot(int)
    def on_tempSB_valueChanged(self, p0):
        self.temp = p0
        self.calcColor()
