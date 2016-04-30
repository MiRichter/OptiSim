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
                All rights reserved.
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
    
    
    
    
    
    
