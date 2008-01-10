from libdesklets.controls import Interface, Permission

class ITime(Interface):

    # properties along with their permissions
    time = Permission.READ
    date = Permission.READ
    ticks = Permission.READ
    timezone = Permission.READWRITE
