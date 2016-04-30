#The complete source code for mplwidget.py is:
# Python Qt5 bindings for GUI objects
from PyQt5 import QtGui, QtWidgets
# import the Qt5Agg FigureCanvas object, that binds Figure to
# Qt5Agg backend. It also inherits from QWidget
import matplotlib as MPL
MPL.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# Matplotlib Figure object
from matplotlib.figure import Figure



class MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self):
        # setup Matplotlib Figure and Axis after defining standard font properties
        font = {'family' : 'serif',
                'weight' : 'bold',
                'size'   : 8}
        axes = {'labelsize' : 12, 
                'labelcolor' : 'green'}

        #MPL.rc('font', **font)  # pass in the font dict as kwargs
        #MPL.rc('axes', **axes)
        MPL.rcParams['figure.facecolor'] = 'white'
        MPL.rcParams['figure.autolayout'] = 'TRUE'
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvas.setSizePolicy(self,
        QtWidgets.QSizePolicy.Preferred,
        QtWidgets.QSizePolicy.Preferred)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)

class MplWidgetSimple(QtWidgets.QWidget):
    """Widget defined in Qt Designer"""
    def __init__(self, parent = None):
        # initialization of Qt MainWindow widget
        QtWidgets.QWidget.__init__(self, parent)
        # set the canvas to the Matplotlib widget
        self.canvas = MplCanvas()
        ## create a vertical box layout
        self.vbl = QtWidgets.QVBoxLayout()
        # add TabWidget to vertical box
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
