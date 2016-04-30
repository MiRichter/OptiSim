from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon


from ui.mainwindow import MainWindow, __version__

import ui.mainwindow
import qrc_resource
import sys
import time
import traceback
import io
import os
from PyQt5 import QtGui, QtWidgets


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
    errorbox = QtWidgets.QMessageBox()
    errorbox.setText(str(notice)+str(msg))
    errorbox.exec_()
    
sys.excepthook = excepthook

def main():

    app = QApplication(sys.argv)
    app.setOrganizationName("University of Oldenburg")
    app.setOrganizationDomain("www.uni-oldenburg.de")
    app.setApplicationName("OptiSim")
    app.setWindowIcon(QIcon(":/OS_logo.png"))
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    

