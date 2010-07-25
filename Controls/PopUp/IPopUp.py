from libdesklets.controls import Interface, Permission

class IPopUp(Interface):
  text    = Permission.WRITE
  icon    = Permission.WRITE
  buttons = Permission.WRITE

  visible = Permission.READWRITE

  event   = Permission.READ
  error   = Permission.READ
  status  = Permission.READ

