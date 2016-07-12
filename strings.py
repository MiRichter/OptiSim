'''
file to sum standardized strings used for OptiSim
'''
import numpy
import scipy
import matplotlib
import colorpy
import platform
from PyQt5 import QtCore

def about(__version__):
    string = """<b>OptiSim</b> Version {} by Michael Richter
                <p>Copyright &copy; 2016-04 University of Oldenburg. 
                Published under GNU General Public Licence V3 (see licence file).
                <p>This application can be used to perform
                optical simulations.
                <p>Based partly on the work of Volker Lorrmann & Steve Byrnes. Color tool based on ColorPy by Mark Kness.
                """.format(__version__)
    versionsString = """<p>Python {} - Qt {} - PyQt {} - Numpy {} - Scipy {} - Matplotlib {} - Colorpy {} on {}""".format(platform.python_version(),
                QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, numpy.version.version, scipy.__version__, matplotlib.__version__, '0.1.0 for Python 3',
                platform.system())
    return string, versionsString
    

def startLog(version):
    separator = '*' * 58
    Title = '''*  _____           __        ____                        *
* /\  __`\        /\ \__  __/\  _`\   __                 *
* \ \ \/\ \  _____\ \ ,_\/\_\ \,\L\_\/\_\    ___ ___     *
*  \ \ \ \ \/\ '__`\ \ \/\/\ \/_\__ \\\/\ \ /' __` __`\   *
*   \ \ \_\ \ \ \L\ \ \ \_\ \ \/\ \L\ \ \ \/\ \/\ \/\ \  *
*    \ \_____\ \ ,__/\ \__\\\ \_\ `\____\ \_\ \_\ \_\ \_\ *
*     \/_____/\ \ \/  \/__/ \/_/\/_____/\/_/\/_/\/_/\/_/ *
*              \ \_\                                     *
*               \/_/                                     *'''
    #Title = 'OptiSim'
    Version = '*' + ' '*21 + 'Version ' + version + ' '*22 + '*'
    Name = '*' + ' '*19 + 'by Michael Richter' + ' '*19 + '*'
    _, versions = about(version)
    Versions = 'tools used: {}'.format(str(versions))
    sections = [separator, Title, Version, Name, separator, '', Versions]
    msg = '\n'.join(sections)
    return msg
    
def endLog(time):
    end = '\n... done successfully!'
    separator = '*' * 58
    Time = '*  Finished after %.4f s' % time + ' '*31 + '*'
    thanks = '*  Thank you for using OptiSim!' + ' '*26 + '*'
    sections = [end, '', separator, Time, thanks, separator]
    msg = '\n'.join(sections)
    return msg
    

def styleSheetMainWindow():
    return """
        QMainWindow{
        background-color: white
        }
        QWidget{
        background-color: white;
        }
        QMainWindow::separator {
        background: lightblue;
        width: 3px; /* when vertical */
        height: 3px; /* when horizontal */
        }
        QMainWindow::separator:hover {
        background: darkblue;
        }
        QPushButton:hover{
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 rgb(82,169,248), stop: 1 rgb(147,219,251));
        }
        QDockWidget::title {
        background: rgb(222,244,254);
        }
        QLineEdit{
        border: 1px solid rgb(0,103,176);
        border-radius: 5px;
        margin: 2px;
        }
        QSpinBox{
        border: 1px solid rgb(0,103,176);
        border-radius: 5px;
        }
        QDoubleSpinBox{
        border: 1px solid rgb(0,103,176);
        border-radius: 5px;
        }
        QComboBox{
        border: 1px solid rgb(0,103,176);
        border-radius: 5px;
        }
        
        QPushButton {
        border: 0px;
        border-radius: 4px;
        background-color: rgb(82,169,248);
        font: bold 12px;
        color: white;
        padding: 6px;
        }
        QPushButton:pressed {
        background-color: rgb(147,219,251);
        }
        QPushButton:flat {
        border: none; /* no border for a flat push button */
        }
        QPushButton:default {
        border-color: navy; /* make the default button prominent */
        }
        QToolBar {
        background: white
        }
        QMenu {
        background-color: white;
        margin: 5px; /* some spacing around the menu */
        }
        QMenu::item {
        padding: 2px 25px 2px 20px;
        border: 2px solid transparent; /* reserve space for selection border */
        }
        QMenu::item:selected {
        border-color: darkblue;
        background: rgb(222,244,254);
        }
        QMenu::icon:checked { /* appearance of a 'checked' icon */
        background: gray;
        border: 1px inset gray;
        position: absolute;
        top: 1px;
        right: 1px;
        bottom: 1px;
        left: 1px;
        }
        QMenu::separator {
        height: 1px;
        background: darkblue;
        margin-left: 2px;
        margin-right: 2px;
        }
        QMenu::indicator {
        width: 20px;
        height: 20px;
        }
        QMenuBar {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 rgb(222,244,254), stop:1 white);
        }
        QMenuBar::item {
        spacing: 3px; /* spacing between menu bar items */
        padding: 1px 4px;
        background: transparent;
        border-radius: 4px;
        }
        QMenuBar::item:selected { /* when selected using mouse or keyboard */
        background: #a8a8a8;
        }
        QMenuBar::item:pressed {
        background: #888888;
        }
        QStatusBar {
        background-color: rgb(222,244,254);
        }
        QStatusBar QLabel {
        border: 3px solid white;
        }
        QListWidget {
        border: 1px solid rgb(0,103,176);
        border-radius: 5px;
        }
        QListWidget:item:selected {
        background-color: rgba(9,128,237,90);
        }
        
        QTabWidget::pane { /* The tab widget frame */
        border: 2px solid rgb(42,141,212);
        border-radius: 4px;
        }
        QTabWidget::tab-bar {
            left: 5px; /* move to the right by 5px */
        }
        /* Style the tab using the tab sub-control. Note that
            it reads QTabBar _not_ QTabWidget */
            
        QTabBar::tab {
            color: white;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 rgb(147,219,251), stop: 1 rgb(82,169,248));
            border-bottom-color: #C2C7CB; /* same as the pane color */
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 8ex;
            padding: 3px;
        }
        
        QTabBar::tab:selected, QTabBar::tab:hover {
            background: rgb(9,128,237);
        }
        """
        
def styleSheetFrame():
    return """
        QFrame {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgb(222,244,254), stop: 1 white);
        border-width: 5px;
        }
        QPushButton {
        border-style: outset;
        border-width: 1px;
        border-radius: 10px;
        border-color: rgb(0, 103, 176);
        font: bold 12px;
        min-width: 8em;
        padding: 6px;
        background: white;
        color: black;
        }
        QPushButton:hover{
        color: blue
        }
        QPushButton:checked{
        border-width: 2px;
        
        }
        """#background: rgb(200,200,200)


# additional stuff
"""
        QScrollArea QWidget {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E0E0E0, stop: 1 #FFFFFF);
        }
        QTabWidget{
        background-color: lightgrey;
        border: 2px solid gray;
        border-radius: 5px;
        margin-top: 1ex; /* leave space at the top for the title */
        }
        QPushButton {
        border-style: inset;
        border-width: 1px;
        border-radius: 1px;
        border-color: black;
        font: bold 12px;
        min-width: 8em;
        padding: 6px;
        background: yellow;
        color: black;
        }
                
        QGroupBox {
        border: 2px solid gray;
        border-radius: 5px;
        margin-top: 1ex; /* leave space at the top for the title */
        }
        QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center; /* position at the top center */
        padding: 0 3px;
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #FFOECE, stop: 1 #FFFFFF);
        }
        QGroupBox::indicator {
        width: 13px;
        height: 13px;
        }

        QLineEdit {
        background-color: white;
        border: 2px solid gray;
        border-radius: 5px;
        padding: 0 8px;
        selection-background-color: darkgray;
        }

        """
    
    
    
    
    
    
