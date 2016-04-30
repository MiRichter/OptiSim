from PyQt5 import QtGui, QtCore, QtWidgets
import os
from ui.mplwidget import *
from classes.errors import *
from classes.navtoolbar import DraggableLegend

def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            raise LoadError('Can not convert string {} into number!'.format(s))


class Subwindow(MplWidget):
    sequenceNumber = 1

    def __init__(self, title, xAxes, curves, xLabel, yLabel):
        """
        creates a subwindow with title and x-Axes and 
        Dictionary of names and y-values of curves to plot
        """
        super(Subwindow, self).__init__()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.isUntitled = True
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 10, 10)
        self.ax = self.canvas.ax
    
        self.curves = curves
        self.xLabel = xLabel
        self.xAxes = xAxes
    
        self.setData()
        #self.dataTable.resizeColumnsToContents()
        #self.dataTable.resizeRowsToContents()
         
        for name in sorted(list(curves.keys())):
            line = self.plot(xAxes, curves[name], name)
        
        self.ax.set_xlabel(xLabel)
        self.ax.set_ylabel(yLabel)
        legend = self.ax.legend()
        self.legend = DraggableLegend(legend)
        
        self.canvas.draw()
        
        
    def plot(self, x, y, curvetitle):
        """Plot a x-y-curve with label curvetitle"""
        axis = self.canvas.ax
        # clear the Axes
        #axis.clear()
        # draw a line plot with picker tolerance 5, and name curve for legend
        
        if 'reference' in curvetitle:
            line, = axis.plot(x, y,  picker=5, label=curvetitle, linestyle='None', marker='o', markersize=2)
        else:
            line, = axis.plot(x, y,  picker=5, label=curvetitle)
        
        # reset the X limits
        #axis.set_xlim(xmin=x[0], xmax=x[-1])
        # set the X ticks & tickslabel as the letters
        #axis.set_xticks(range(len(x)))
        #labelx.set_fontsize(13)
        # enable grid only on the Y axis
        axis.get_yaxis().grid(True)
        # force an image redraw
        return line
        
    def setData(self):
        
        self.dataTable.setColumnCount(len(self.curves) + 1)
        self.dataTable.setRowCount(len(self.xAxes))
        horHeaders = [self.xLabel]
        for xIndex, xValue in enumerate(self.xAxes):
            newItem = QtWidgets.QTableWidgetItem('%.4g' % xValue)
            newItem.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
            self.dataTable.setItem(xIndex, 0, newItem)
        for n, key in enumerate(sorted(self.curves.keys())):
            horHeaders.append(key)
            for m, item in enumerate(self.curves[key]):
                newItem = QtWidgets.QTableWidgetItem('%g' % item)
                newItem.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
                self.dataTable.setItem(m, n + 1, newItem)
        self.dataTable.setHorizontalHeaderLabels(horHeaders)
        
    
    def saveData(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save data to file', '','data files (*.dat)')
        if fname:
            try:
                f = open(fname, 'w')
                f.write(self.xLabel + '\t')
                for value in self.curves.keys():
                    f.write(value + '\t')
                f.write('\n')
                for i in range(len(self.xAxes)):
                    f.write(str(self.xAxes[i]))
                    for key in self.curves.keys():
                        f.write('\t{}'.format(str(self.curves[key][i])))
                        #f.write('\t')
                    f.write('\n')                
                f.close()
            except IOError as e:
                raise WriteError("Could not write data to file {}: \n {}".format(fname, e.args[1]))
    
    def loadCurve(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName()
        # if a file is selected
        if file:
            x = []
            y = []
            with open(file) as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line[0].isdigit():
                        fields = line.split("\t")
                        x.append(num(fields[0]))
                        y.append(num(fields[1]))
            f.close()
            head, tail = os.path.split(file)
            line = self.plot(x, y, tail)
            self.ax.legend_ = None
            legend = self.ax.legend()
            self.legend = DraggableLegend(legend)
            self.canvas.draw()
            
            #fm = plt.get_current_fig_manager()
            #fm.toolbar.actions()[0].triggered.connect(home_callback)
