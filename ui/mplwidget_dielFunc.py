#The complete source code for mplwidget.py is:
# Python Qt4 bindings for GUI objects
from PyQt5 import QtWidgets, QtGui,  QtCore

# Matplotlib Figure object
from matplotlib.figure import Figure
import matplotlib as MPL
MPL.use("Qt5Agg")
# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
#import matplotlib.pyplot as plt

class MplWidgetDielFunc(QtWidgets.QWidget):
    """Widget defined in Qt Designer"""
    def __init__(self, parent = None):
        # initialization of Qt MainWindow widget
        QtWidgets.QWidget.__init__(self, parent)
        # set the canvas to the Matplotlib widget
        self.canvas = MplCanvas()
        ## create a vertical box layout
        self.vbl = QtWidgets.QVBoxLayout()
        
        self.tab = QtWidgets.QTabWidget()
        self.tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        
        self.dataTable = QtWidgets.QTableWidget()
        self.tlb = NavToolBar(self.canvas, self)
        
        self.tab.addTab(self.canvas, 'curves')
        self.tab.addTab(self.dataTable, 'data')

        self.vbl.addWidget(self.tlb)
        self.vbl.addWidget(self.tab)
        self.setLayout(self.vbl)
        
        self.ax = self.canvas.ax
        
        self.clip = QtWidgets.QApplication.clipboard()
    
    def showCurves(self, xAxes, curves, xLabel, yLabel):
        # fill data table
        self.setData(xLabel, xAxes, curves)
        
        self.ax.clear()
        
        # plot curves
        for name, curve in curves.items():
            self.plot(xAxes, curve, name)
        
        self.ax.set_xlabel(xLabel)
        self.ax.set_ylabel(yLabel)
        legend = self.ax.legend()
        DraggableLegend(legend)
        
        self.canvas.draw()

    def plot(self, x, y, curvetitle):
        axis = self.canvas.ax
        # clear the Axes
        #axis.clear()
        # make dates as x values
        #dates = MPL.dates.date2num(x)
        # draw a line plot with picker tolerance 5, and name curve for legend
        axis.plot(x, y,  picker=5, label=curvetitle)
        axis.get_yaxis().grid(True)
        # force an image redraw
        #self.canvas.draw()
        
    def setData(self, xLabel, x, curves):
        self.dataTable.clear()
        self.dataTable.setColumnCount(len(curves) + 1)
        self.dataTable.setRowCount(len(x))
        horHeaders = [xLabel]
        for xIndex, xValue in enumerate(x):
            newItem = QtWidgets.QTableWidgetItem(str(xValue))
            self.dataTable.setItem(xIndex, 0, newItem)
        for n, key in enumerate(sorted(curves.keys())):
            horHeaders.append(key)
            for m, item in enumerate(curves[key]):
                newItem = QtWidgets.QTableWidgetItem('%g' % item)
                self.dataTable.setItem(m, n + 1, newItem)
        self.dataTable.setHorizontalHeaderLabels(horHeaders)

    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            selected = self.dataTable.selectedRanges()

            if e.key() == QtCore.Qt.Key_C: #copy
                s = ""

                for r in range(selected[0].topRow(), selected[0].bottomRow()+1):
                    for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                        try:
                            s += str(self.dataTable.item(r,c).text()) + "\t"
                        except AttributeError:
                            s += "\t"
                    s = s[:-1] + "\n" #eliminate last '\t'
                self.clip.setText(s)

class MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self):
        # setup Matplotlib Figure and Axis after defining standard font properties
        font = {'family' : 'serif',
                'weight' : 'bold',
                'size'   : 10}
        axes = {'labelsize' : 12, 
                'labelcolor' : 'black'}

        #MPL.rc('font', **font)  # pass in the font dict as kwargs
        #MPL.rc('axes', **axes)
        MPL.rcParams['figure.facecolor'] = 'white'
        MPL.rcParams['figure.autolayout'] = 'TRUE'
        #MPL.rcParams['backend.qt5'] = 'Qt5Agg'
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvas.setSizePolicy(self,
        QtWidgets.QSizePolicy.Expanding,
        QtWidgets.QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)



class NavToolBar(NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]



class DraggableLegend:
    """
    A simple class to have a draggable legend in the plots. Just click on the legend,
    drag it and release the click.
    """

    def __init__(self, legend):
        self.legend = legend
        self.gotLegend = False
        legend.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        legend.figure.canvas.mpl_connect('pick_event', self.on_pick)
        legend.figure.canvas.mpl_connect('button_release_event', self.on_release)
        legend.set_picker(self.my_legend_picker)

    def on_motion(self, evt):
        if self.gotLegend:
            dx = evt.x - self.mouse_x
            dy = evt.y - self.mouse_y
            loc_in_canvas = self.legend_x + dx, self.legend_y + dy
            loc_in_norm_axes = self.legend.parent.transAxes.inverted().transform_point(loc_in_canvas)
            self.legend._loc = tuple(loc_in_norm_axes)
            self.legend.figure.canvas.draw()

    def my_legend_picker(self, legend, evt): 
        return self.legend.legendPatch.contains(evt)   

    def on_pick(self, evt): 
        if evt.artist == self.legend:
            bbox = self.legend.get_window_extent()
            self.mouse_x = evt.mouseevent.x
            self.mouse_y = evt.mouseevent.y
            self.legend_x = bbox.xmin
            self.legend_y = bbox.ymin 
            self.gotLegend = 1

    def on_release(self, event):
        if self.gotLegend:
            self.gotLegend = False
