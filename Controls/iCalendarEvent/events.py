try:
    from gamin import GAMChanged, GAMCreated, GAMMoved, GAMDeleted
except:
    GAMChanged = 0
    GAMCreated = 1
    GAMMoved   = 2
    GAMDeleted = 3

FILE_CHANGED = GAMChanged
FILE_CREATED = GAMCreated
FILE_MOVED   = GAMMoved
FILE_DELETED = GAMDeleted
