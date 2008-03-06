from libdesklets.controls import Interface, Permission

class IRandom(Interface):

    # properties along with their permissions
    randrange = Permission.READ
    randint = Permission.READ
    choice = Permission.READ
    sample = Permission.READ
    random = Permission.READ
    uniform = Permission.READ
    betavariate = Permission.READ
    expovariate = Permission.READ
    gammavariate = Permission.READ
    gauss = Permission.READ
    lognormvariate = Permission.READ
    normalvariate = Permission.READ
    vonmisesvariate = Permission.READ
    paretovariate = Permission.READ
    weibullvariate = Permission.READ
    sequence = Permission.READWRITE

