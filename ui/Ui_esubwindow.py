from PyQt5 import QtGui, QtCore, QtWidgets

from ui.mplwidget import *
from .econtroller import eController
from classes.navtoolbar import NavToolBar as NavigationToolbar
from classes.navtoolbar import DraggableLegend

import numpy as np
#from matplotlib.mlab import griddata
#from scipy.interpolate import griddata

def format_coord(x, y):
    col = int(x+0.5)
    row = int(y+0.5)
    if col>=0 and col<numcols and row>=0 and row<numrows:
        z = X[row,col]
        return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
    else:
        return 'x=%1.4f, y=%1.4f'%(x, y)

        
class ESubwindow(MplWidget):
    
    def __init__(self, wvl, step, curves, ylabel):
        """
        creates a subwindow with title and x-Axes and 
        Dictionary of names and y-values of curves to plot
        """
        super(ESubwindow, self).__init__()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.controller = eController()
        self.hbl.addWidget(self.controller)
        self.canvas2D = MplCanvas()
        self.plot2Dbutton = QtWidgets.QPushButton()
        self.plot2Dbutton.setText('show 2D plot')
        self.plot2Dbutton.clicked.connect(self.show2Dplot)
        self.vbl.addWidget(self.plot2Dbutton)
        
        self.controller.wavelengthSB.setRange(np.min(wvl), np.max(wvl))
        self.controller.wavelengthSB.setSingleStep(step)
        self.controller.wavelengthSB.setValue(np.min(wvl))
        self.controller.wavelengthSlider.setRange(np.min(wvl), np.max(wvl))
        self.controller.wavelengthSlider.setValue(np.min(wvl))
        self.controller.wavelengthSlider.setSingleStep(step)
        self.controller.wavelengthSlider.setPageStep(step)
        self.controller.wavelengthSB.valueChanged.connect(self.updatePlot)
        self.controller.wavelengthSlider.valueChanged.connect(self.updatePlot)
        
        self.ax = self.canvas.ax
        #self.ax2d = self.canvas2D.ax
        
        self.curves = curves # format: {'curve name': [array(x-vector), 2Darray()]}
        self.x = curves[list(curves.keys())[0]][0]
        self.step = step
        self.wvl = wvl
        self.idx = 1
        self.wvlset = wvl[self.idx]
    
        self.setData()
        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()
        
        self.init = True
        self.lines = []
        self.plot()
        #self.plot2d()
        
        self.ax.set_xlabel('depth (nm)')
        self.ax.set_ylabel(ylabel)
        legend = self.ax.legend()
        self.legend = DraggableLegend(legend)
        
    def plot(self):
            
        if self.init == True:
            # this should only be executed on the first call to updateData
            self.ax.hold(True)
            for i, name in enumerate(self.curves.keys()):
                x = self.x
                label = name + ' ' + str(self.wvl[self.idx]) + ' nm'
                data = self.curves[name][1][self.idx]
                self.ax.plot(x, data,  picker=5, label=label)
                #TODO: make variable ylim (log for generation)
                self.ax.set_ylim(0, np.max(data))
            #self.canvas.ax.grid()
            self.init = False
        else:
            # now we only modify the plotted line
            #self.ax.clear()
            for i, line in enumerate(self.ax.lines):
                name = list(self.curves.keys())[i]
                data = self.curves[name][1][self.idx]
                self.ax.set_ylim(0, np.max(data))
                line.set_ydata(data)
                label = name + ' ' + str(self.wvl[self.idx]) + ' nm'
                self.legend.legend.get_texts()[i].set_text(label)
            
        self.canvas.draw_idle() 
    
    def show2Dplot(self):
        window = QtWidgets.QDialog(self)
        vbl = QtWidgets.QVBoxLayout(window)
        canvas2D = MplCanvas()
        ntb = NavigationToolbar(canvas2D, window)
        vbl.addWidget(ntb)
        vbl.addWidget(canvas2D)
        X, Y = np.meshgrid(self.x, self.wvl)
        name = list(self.curves.keys())[0]
        Z = np.array(self.curves[name][1])
        canvas2D.ax.pcolor(X, Y, Z)
        # adapt data label:
        self.numrows, self.numcols = Z.shape
        #canvas2D.ax.format_coord = format_coord        
        window.exec_()
    

        
    def plot2d(self):
        X, Y = np.meshgrid(self.x, self.wvl)
        #define grid.
        x0 = self.x[0]
        x1 = self.x[-1]
        y0 = self.wvl[0]
        y1 = self.wvl[-1]
        x = np.linspace(x0,x1,100)
        y = np.linspace(y0,y1,100)
        xi, yi = np.meshgrid(x, y)
        xi, yi = np.mgrid[x0:x1:100j, y0:y1:100j]
        # grid the data.
        #points = np.random.rand(100, 2)
        #Einterp = griddata(self.x, self.wvl, self.E, x, y, interp='linear')
        name = list(self.curves.keys())[0]
        self.ax2d.pcolor(X, Y, np.array(self.curves[name][1]))
            #Einterp,# aspect='auto', 
             #           extent=[x0, x1, 
              #                  y0, y1]
                        #interpolation='nearest'
               #         )
        self.canvas2D.draw()
    
    def setData(self):
        self.dataTable.setColumnCount(len(self.curves) + 1)
        self.dataTable.setRowCount(len(self.x))
        self.horHeaders = ['depth (nm)']
        for i, x in enumerate(self.x):
            newXItem = QtWidgets.QTableWidgetItem('%.4f' % x)
            newXItem.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
            self.dataTable.setItem(i, 0, newXItem)
        for j, curve in enumerate(self.curves.keys()):
            self.horHeaders.append(curve)
            for k, item in enumerate(self.curves[curve][1][self.idx]):
                newYItem = QtWidgets.QTableWidgetItem('%.4f' % item)
                newYItem.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
                self.dataTable.setItem(k, j+1, newYItem)
        self.dataTable.setHorizontalHeaderLabels(self.horHeaders)
        
    def updateData(self):
        for i, curve in enumerate(self.curves.keys()):
            for k, value in enumerate(self.curves[curve][1][self.idx]):
                self.dataTable.item(k, i+1).setText('%.4f' % value)
    
    def saveData(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save data to file', '','data files (*.dat)')
        if fname:
            f = open(fname, 'w')
            f.write('\t'.join(self.horHeaders))
            #for value in self.curves.keys():
            #    f.write(value + '\t')
            f.write('\n')
            for i in range(len(self.x)):
                f.write(''.join(str(self.x[i])) + '\t')
                for key in self.curves.keys():
                    f.write(''.join(str(self.curves[key][1][self.idx][i])) + '\t')
                f.write('\n')                
            f.close()

    def updatePlot(self, int):
        if int % self.step > 0:
            int = int - (int % self.step)
            self.controller.wavelengthSB.setValue(int)
        self.idx = np.nonzero(self.wvl == int)[0][0]
        #self.wvlset = int
        #self.Eset = self.E[idx] 
        self.updateData()
        self.plot()
