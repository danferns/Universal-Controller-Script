
from common.eventpattern import BasicEventPattern, fromNibbles
from controlsurfaces import PitchWheel
from controlsurfaces.valuestrategies import Data2Strategy

class HammerPitchWheel(PitchWheel):
    """
    Implementation of the pitch wheel on the Hammer 88 Pro since its behaviour
    is weird
    """
    def __init__(self) -> None:
        super().__init__(
            BasicEventPattern(fromNibbles(0xE, ...), (0x0, 0x7F), ...),
            Data2Strategy()
        )