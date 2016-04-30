#The complete source code for mplwidget.py is:
# Python Qt4 bindings for GUI objects
from PyQt5 import QtGui, QtCore, QtWidgets
# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
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

class MplWidget(QtWidgets.QWidget):
    """Widget defined in Qt Designer"""
    def __init__(self, parent = None):
        # initialization of Qt MainWindow widget
        QtWidgets.QWidget.__init__(self, parent)
        # set the canvas to the Matplotlib widget
        self.canvas = MplCanvas()
        
        ## create a vertical box layout
        self.hbl = QtWidgets.QHBoxLayout()
        self.vbl = QtWidgets.QVBoxLayout()
        self.loadButton = QtWidgets.QPushButton('load curve')
        self.loadButton.setMaximumWidth(100)
        self.loadButton.clicked.connect(self.loadCurve)
        self.labelLayout = QtWidgets.QHBoxLayout()
        # create Labels to show data points from picker
        self.curveLabel = QtWidgets.QLabel('curve: ')
        self.dataLabel = QtWidgets.QLabel('data point: ')
        self.labelLayout.addWidget(self.curveLabel)
        self.labelLayout.addWidget(self.dataLabel)
        self.labelLayout.addWidget(self.loadButton)
        
        self.vbl.addLayout(self.labelLayout)
        # create a tabWidget as central widget
        self.tab = QtWidgets.QTabWidget()
        # add TabWidget to vertical box
        self.hbl.addWidget(self.tab)
        # add mpl Widget to vertical box
        self.tab.addTab(self.canvas, 'curves')
        # add a tab for data table
        self.dataTable = QtWidgets.QTableWidget()
        self.tab.addTab(self.dataTable, 'data')
        # set the layout to th vertical box
        self.vbl.addLayout(self.hbl)
        
        self.setLayout(self.vbl)
        
        self.clip = QtWidgets.QApplication.clipboard()
        
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        
    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        thisline = event.artist
        if thisline is not self.legend.legend:
            xdata, ydata = thisline.get_data()
            ind = event.ind
            self.curveLabel.setText('curve: {}'.format(thisline.get_label()))
            self.dataLabel.setText('selected point: x = {}  y = {}'.format(xdata[ind[0]], ydata[ind[0]]))

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
    
    def loadCurve(self):
        pass
