import gtk


class StatusBar(gtk.Statusbar):
    
    def __init__(self):
        super(StatusBar, self).__init__()
        self.set_has_resize_grip(True)
        self.push(0, 'All ready')
        # self.__construct_statusbar()


    def set_msg(self, msg):
        self.pop(0)
        self.push(0, msg)
    
    def __construct_statusbar(self):
        # create a stack of basic startup messages which can be easily popped while loading
        self.push(0, 'All ready')
        self.push(0, 'Building')
        self.push(0, 'Looking for news')
        self.push(0, 'Looking for local controls')
        self.push(0, 'Looking for local desklets')
        self.push(0, 'Looking for remote controls')
        self.push(0, 'Looking for remote desklets')