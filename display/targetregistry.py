#
# Registry for DataTargets. To add a new target just add an appropriate entry
# to _REGISTRY.
#

from TargetAlignment     import TargetAlignment
from TargetArray         import TargetArray
from TargetDisplay       import TargetDisplay
from TargetEntry         import TargetEntry
from TargetExpander      import TargetExpander
from TargetFrame         import TargetFrame
from TargetGauge         import TargetGauge
from TargetGroup         import TargetGroup
from TargetImage         import TargetImage
from TargetLabel         import TargetLabel
from TargetBonoboControl import TargetBonoboControl
from TargetCanvas        import TargetCanvas
from TargetPlotter       import TargetPlotter

_targets = {
    "alignment" : (TargetAlignment, True),
    "array"     : (TargetArray, False),
    "display"   : (TargetDisplay, False),
    "entry"     : (TargetEntry, False),
    "expander"  : (TargetExpander, True),
    "frame"     : (TargetFrame, True),
    "gauge"     : (TargetGauge, True),
    "group"     : (TargetGroup, False),
    "image"     : (TargetImage, False),
    "label"     : (TargetLabel, False),
    "canvas"    : (TargetCanvas, False),
    "embed"     : (TargetBonoboControl, False),
    "plotter"   : (TargetPlotter, False)
}


#
# Creates and returns the given target.
#
def create(name, parent):

    try:
        clss, one_child = _targets[name]
    except KeyError:
        raise UserError(_("Unknown element <b>&lt;%s&gt;</b>") % name,
                        _("Either there is a typo in the .display file "
                          "or you have an incompatible version of gDesklets."))

    obj = clss(name, parent)
    return obj


#
# Returns whether the given container accepts more than one children.
#
def one_child(name):

    clss, one_child = _targets[name]
    return one_child

