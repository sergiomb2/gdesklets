from plugin.Interface import Interface
from plugin import Permission


class ISensor(Interface):

    sensor = Permission.WRITE
    action = Permission.WRITE
    config_id = Permission.WRITE
    stop = Permission.WRITE
    output = Permission.READ
    menu = Permission.READ
    configurator = Permission.READ
