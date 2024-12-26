import gtk


class ToolBar(gtk.Toolbar):
    
    def __init__(self, main_window):
        super(ToolBar, self).__init__()
        
        self.__action_group = main_window.get_action_group()
        
        self.insert( self.__action_group.get_action("install").create_tool_item(), 0 )
        self.insert( self.__action_group.get_action("remove").create_tool_item(), 1 )
        self.insert( self.__action_group.get_action("activate").create_tool_item(), 2 )
        # toolbar.insert( self.__action_group.get_action("deactivate").create_tool_item(), 3 )
        # toolbar.insert( self.__action_group.get_action("update").create_tool_item(), 3 )
        self.insert( self.__action_group.get_action("quit").create_tool_item(), 3 )
        
