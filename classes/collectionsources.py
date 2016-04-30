from PyQt4 import QtGui, QtCore

class CollectionWidget(QtGui.QWidget):
    '''
    class to display collection function widget to specify 
        - constant collection
        - linear collection function vs. depth
        - custom function 
    '''
    
    def __init__(self, layer, callback):

        super(CollectionWidget, self).__init__()
        
        self.collection = layer.collection
        
        self.ok = None
        self.setupUi()
        
        self.fillEditField()
        
        self.callback = callback
        
        
        
    def setupUi(self):
        
        HLayout = QtGui.QHBoxLayout(self)
        Label = QtGui.QLabel('collection function:')
        self.Input = QtGui.QLineEdit()
        HLayout.addWidget(Label)
        HLayout.addWidget(self.Input)
        
        self.Input.editingFinished.connect(self.uptdateCollection)
    
        self.Input.textChanged.connect(self.checkState)
        # emit the signal one time for init
        self.Input.textChanged.emit(self.Input.text())
        
    def fillEditField(self):
        mode = self.collection['mode']
        value = self.collection['value']
        
        if mode == 'constant':
            self.Input.setText(str(value))
        if mode == 'linear':
            self.Input.setText('lin(%f,%f)' %(value[0], value[1]))
    
    def uptdateCollection(self):
        if self.ok == 'constant':
            input = self.Input.text()
            self.collection['mode'] = 'constant'
            self.collection['value'] = float(input)
            self.callback(self.collection)
        elif self.ok == 'linear':
            input = self.Input.text()
            self.linearExp.indexIn(input)

            a = self.linearExp.cap(1)
            b = self.linearExp.cap(2)

            self.collection['mode'] = 'linear'
            self.collection['value'] = [float(a), float(b)]
            self.callback(self.collection)
        
    def checkState(self, *args, **kwargs):        
        sender = self.sender()
        constantVal = QtGui.QDoubleValidator()
        #\\b(lin|LIN|Lin)\\b
        #decimal: ^(?:0|[1-9][0-9]*)\.[0-9]+$
        self.linearExp = QtCore.QRegExp("lin[\\(]([+-]?\\d*\\.?\\d+),\s*([+-]?\\d*\\.?\\d+)[\\)]")
        linearVal = QtGui.QRegExpValidator(self.linearExp)
        
        constState = constantVal.validate(sender.text(), 0)[0]
        linState = linearVal.validate(sender.text(), 0)[0]

        if constState == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
            self.ok = 'constant'
        elif linState == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
            self.ok = 'linear'
            self
        elif constState == QtGui.QValidator.Intermediate or \
           linState == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
            self.ok = None
        else:
            color = '#f6989d' # red
            self.ok = None
        
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
