from libdesklets.controls import Interface, Permission

class IURI(Interface):
    
    file     = Permission.READWRITE
    raw      = Permission.READ
    stripped = Permission.READ
    splitted = Permission.READ
