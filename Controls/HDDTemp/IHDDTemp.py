from libdesklets.controls import Interface, Permission

class IHDDTemp(Interface):

    # properties along with their permissions
    available_devices = Permission.READ
    poll_all = Permission.READ
    
    device = Permission.READWRITE
    poll = Permission.READ
