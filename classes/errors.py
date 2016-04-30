''' Definition of application specific error Values'''

class LoadError(Exception):
    def __init__(self, message):
        self.msg = message #'<span style="color:#FF0000">File load ERROR:</span>\n' + 

class WriteError(Exception):
    def __init__(self, message):
        self.msg = '<b>File write ERROR:</b>\n' + message
    
class NotImplementedError(Exception):
    def __init__(self, message):
        self.msg = message
        
class OutOfRangeError(Exception):
    def __init__(self, message):
        self.msg = message
        
