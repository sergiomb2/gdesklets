SUBDIRS = man   \
          basic

SYNOPSIS = python2.2 /usr/bin/synopsis
SYN_FLAGS = -Wc,parser=Python,formatter=HTML,linker=Linker
SYN_SRC = gdesklets */*.py */*/*.py
SYN_DEST = doc/source


doc:
	cd .. && \
	$(SYNOPSIS) $(SYN_FLAGS) -o $(SYN_DEST) $(SYN_SRC)
