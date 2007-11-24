from Widget import Widget
import Settings

class Control(Widget):
    
    def __init__(self, name, description, authors):
        super(Control, self).__init__(name, description, authors)
        self._install_parent_dir = Settings.get_setting('control_install_dir')
        
        
    
    def update(self, new):
        super(Control, self).update(new)
        
        
        
    def __str__(self):
        return super(Control, self).__str__()