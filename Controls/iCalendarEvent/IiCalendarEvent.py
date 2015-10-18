from libdesklets.controls import Interface, Permission

class IiCalendarEvent(Interface):

    # properties along with their permissions
    uri          = Permission.READWRITE
    month        = Permission.READWRITE
    events       = Permission.READ
    new_event    = Permission.WRITE
    delete_event = Permission.WRITE
    #error        = Permission.READWRITE
