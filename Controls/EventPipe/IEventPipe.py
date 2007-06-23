from libdesklets.controls import Interface, Permission

class IEventPipe(Interface):

    subscriptions = Permission.READWRITE
    event = Permission.READWRITE
