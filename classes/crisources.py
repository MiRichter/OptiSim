from PyQt4 import QtGui, QtCore

class DataBaseWidget(QtGui.QWidget):
    '''
    class to display database 
    '''
    #create custom signal (not used) handle callback instead
    #DBIndexChanged = QtCore.pyqtSignal(str)
    
    def __init__(self, layer, database, callback):

        super(DataBaseWidget, self).__init__()
        
        self.layer = layer
        self.Materials = database
        
        self.callback = callback
        
        self.setupUi()
        
    def setupUi(self):
        
        VLayoutDB = QtGui.QVBoxLayout(self)
        self.DBList = QtGui.QListWidget()
        self.DBList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.DBList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.DBList.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        
        self.DBList.addItems(self.Materials)
        MaterialLabel = QtGui.QLabel('Material:')
        VLayoutDB.addWidget(MaterialLabel)
        VLayoutDB.addWidget(self.DBList)
        
        DBItem = self.DBList.findItems(self.layer.criDBName, QtCore.Qt.MatchFixedString)
        self.DBList.setCurrentItem(DBItem[0])
        
        self.DBList.currentItemChanged.connect(self.criDBChanged)
    
    def criDBChanged(self, Item):
        #self.DBIndexChanged.emit(Item.text())
        self.callback(Item.text())
        
    def criDBClicked(self):
        """
        origin of n and k values and displey criSourceWidget funktions
        """
        if self.criFromDB.isChecked():
            self.FileFrame.hide()
            self.ConstantFrame.hide()
            self.DBFrame.show()
     
        
        
class FromFileWidget(QtGui.QWidget):
    '''
    class to display widget 'from file' 
    '''
    def __init__(self, layer, callback):

        super(FromFileWidget, self).__init__()
        
        self.path = layer.criFile['path']        
        self.alpha = layer.criFile['alpha']        
        self.n = layer.criFile['n']
        self.callback = callback

        self.setupUi()


    def setupUi(self):
        VLayout = QtGui.QVBoxLayout(self)
        HLayoutFile = QtGui.QHBoxLayout()
        FileLabel = QtGui.QLabel('file:')
        self.FilePathName = QtGui.QLineEdit()
        
        self.criFilePathButton = QtGui.QPushButton('...')
        
        HLayoutFile.addWidget(FileLabel)
        HLayoutFile.addWidget(self.FilePathName)
        HLayoutFile.addWidget(FilePathButton)
        
        self.alphaGroupBox = QtGui.QGroupBox()
        self.alphaGroupBox.setTitle("alpha only")
        self.alphaGroupBox.setCheckable(True)
        self.alphaGroupBox.setChecked(self.alpha)
        alphaLabel = QtGui.QLabel(self.alphaGroupBox)
        alphaLabel.setText('constant refractive index n:')
        self.spinBox = QtGui.QDoubleSpinBox(self.alphaGroupBox)
        self.spinBox.setProperty("value", self.n)
        self.spinBox.setSingleStep(0.1)
        HLayoutAlpha = QtGui.QHBoxLayout(self.alphaGroupBox)
        HLayoutAlpha.addWidget(alphaLabel)
        HLayoutAlpha.addWidget(self.spinBox)
        
        VLayout.addLayout(HLayoutFile)
        VLayout.addWidget(self.alphaGroupBox)
        
        if self.path:
            self.FilePathName.setText(self.path) 

        FilePathButton.clicked.connect(self.selectCRIFilePath)
        self.alphaGroupBox.toggled.connect(self.updateAlpha)
        self.spinBox.valueChanged.connect(self.updateAlpha)
        
    def selectCRIFilePath(self):
        #TODO: make LineEdit editable for costum path input
        fileName = QtGui.QFileDialog.getOpenFileName(self)
        if fileName:
            self.path = fileName
            self.FilePathName.setText(fileName)
            criFile = dict( path = self.path,
                            alpha = self.alpha,
                            n = self.n) 
            self.callback(criFile)
    
    def updateAlpha(self):
        self.alpha = self.alphaGroupBox.isChecked()
        self.n = self.spinBox.value()
        criFile = dict( path = self.path,
                        alpha = self.alpha,
                        n = self.n)
        self.callback(criFile)
   
class ConstantWidget(QtGui.QWidget):
    '''
    class to display widget 'from file' 
    '''
    def __init__(self, layer, callback):

        super(ConstantWidget, self).__init__()
        
        self.n = layer.criConstant[0]
        self.k = layer.criConstant[1]
        
        self.callback = callback
        
        self.setupUi()
    
    def setupUi(self):
        
        GridLayoutConstant = QtGui.QGridLayout(self)
        nLabel = QtGui.QLabel('refractive index n:')
        kLabel = QtGui.QLabel('extinction coefiicient k:')
        self.ConstantnEdit = QtGui.QDoubleSpinBox()
        self.ConstantkEdit = QtGui.QDoubleSpinBox()
        # set locale to english for point instead of comma seperator
        self.ConstantnEdit.setLocale(QtCore.QLocale('C'))
        self.ConstantkEdit.setLocale(QtCore.QLocale('C'))
        GridLayoutConstant.addWidget(nLabel, 0, 0)
        GridLayoutConstant.addWidget(kLabel, 1, 0)
        GridLayoutConstant.addWidget(self.ConstantnEdit, 0, 1)
        GridLayoutConstant.addWidget(self.ConstantkEdit, 1, 1)
        #set values from layer properties
        self.ConstantnEdit.setProperty("value", self.n)
        self.ConstantkEdit.setProperty("value", self.k)

        self.ConstantnEdit.valueChanged.connect(self.updateConstant)
        self.ConstantkEdit.valueChanged.connect(self.updateConstant)
        
        
    def updateConstant(self):
        self.n = self.ConstantnEdit.value()
        self.k = self.ConstantkEdit.value()
        
        self.callback([self.n, self.k])
