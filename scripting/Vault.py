def Vault(gold, key = open):

    # open is not accessible from the sandbox

    def unlock(k):
        if k == key: return gold
        raise RuntimeError("Intrusion detected")

    return unlock
