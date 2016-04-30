from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
import qrc_resource

class NavToolBar(NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]


class NavToolBar2(NavigationToolbar2QT):
    """
    This class overloads the NavigationToolbar of matplotlib.
    The original icons are replaced by oxygen ones. It is used to have
    a toolbar over the plots in pyQPCR.
    """

    def __init__(self, canvas, parent, coordinates=True):
        """
        Constructor of NavToolBar

        :param canvas: the matplotlib canvas
        :type canvas: matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg
        :param parent: the parent QWidget
        :type parent: PyQt4.QtGui.QWidget
        :param coordinates: boolean coordinates
        :type coordinates: bool
        """
        NavigationToolbar2QT.__init__(self, canvas, parent, coordinates)
        self.setIconSize(QSize(16, 16))

    def _init_toolbar(self):
        """
        This function is a simple modification of the toolbar 
        definition in order to get the oxygen icons in the matplotib toolbar
        """
        a = self.addAction(QIcon(':/Fig_home.png'), 'Home', self.home)
        a.setToolTip('Reset original view')
#        a = self.addAction(QIcon(':/undo.png'), 'Back', self.back)
#        a.setToolTip('Back to previous view')
#        a = self.addAction(QIcon(':/redo.png'), 'Forward', self.forward)
#        a.setToolTip('Forward to next view')
        self.addSeparator()
        a = self.addAction(QIcon(':/Fig_hand.png'), 'Pan', self.pan)
        a.setToolTip('Pan axes with left mouse, zoom with right')
        a = self.addAction(QIcon(':/Fig_zoom.png'), 'Zoom', self.zoom)
        a.setToolTip('Zoom to rectangle')
        self.addSeparator()
#        a = self.addAction(QIcon(':/settings.png'), 'Subplots',
#                self.configure_subplots)
#        a.setToolTip('Configure subplots')
        a = self.addAction(QIcon(':/Fig_filesave.png'), 'Save',
                self.save_figure)
        a.setToolTip('Save the figure')

        self.buttons = {}

        if self.coordinates:
            self.locLabel = QLabel( "", self )
            self.locLabel.setAlignment(Qt.AlignRight|Qt.AlignTop )
            self.locLabel.setSizePolicy( QSizePolicy(QSizePolicy.Expanding,
                                  QSizePolicy.Ignored))
            labelAction = self.addWidget(self.locLabel)
            labelAction.setVisible(True)

        # reference holder for subplots_adjust window
        self.adj_window = None


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
