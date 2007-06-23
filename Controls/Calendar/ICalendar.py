from libdesklets.controls import Interface, Permission

class ICalendar(Interface):

    day = Permission.READ
    days = Permission.READ
    month = Permission.READ
    months = Permission.READ
    time = Permission.WRITE

