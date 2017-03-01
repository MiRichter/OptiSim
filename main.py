from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap

#from multiprocessing import Pool

from ui.mainwindow import MainWindow, __version__

import ui.mainwindow
import qrc_resource
import sys
import time
import traceback
import io
import os
#from PyQt5 import QtGui, QtWidgets, QtCore


def excepthook(excType, excValue, tracebackobj):
    """
    stolen from ERIC IDE!
    Global function to catch unhandled exceptions.
    
    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    separator = '-' * 80
    logFile = "error.log"
    notice = \
        """An unhandled exception occurred. Please report the problem\n"""\
        """via email to <%s>.\n"""\
        """A log has been written to "%s".\n\nError information:\n""" % \
        ("michael.richter@uni-oldenburg.de", os.getcwd())
    versionInfo="OptiSim Version:\t" + getattr(ui.mainwindow, "__version__")
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")
    
    tbinfofile = io.StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [separator, timeString, versionInfo, separator, errmsg, separator, tbinfo]
    msg = '\n'.join(sections)
    try:
        f = open(logFile, "w")
        f.write(msg)
        f.close()
    except IOError:
        pass
    errorbox = QMessageBox()
    errorbox.setText(str(notice)+str(msg))
    errorbox.exec_()
    
#sys.excepthook = excepthook
   
def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("University of Oldenburg")
    app.setOrganizationDomain("www.uni-oldenburg.de")
    app.setApplicationName("OptiSim")
    app.setWindowIcon(QIcon(":/OS_logo.png"))
    
    # Create and display the splash screen
    #splash_pix = QPixmap(":/OS_logo.png")
    #splash = QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    #splash.setMask(splash_pix.mask())
    #splash.show()
    #app.processEvents()
    
    wnd = MainWindow()
    wnd.show()
    #splash.finish(wnd)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    

