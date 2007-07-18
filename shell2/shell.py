import SlickShell
import control.Assembly

import gtk

if __name__ == "__main__":
    a = control.Assembly.Assembly()
    ss = SlickShell.SlickShell(a)
    gtk.main()