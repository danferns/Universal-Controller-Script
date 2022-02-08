
from typing import Any
from common.util.apifixes import UnsafePluginIndex
from controlsurfaces import ControlShadow, Button

# TODO: Remove repeated code here (maybe use a class decorator with a __call__()
# function?)

def filterButtonLift(func, method:bool=True):
    """
    Filter out button lifts so that only presses are processed

    ### Args:
    * `func` (`EventCallback`): Function to decorate
    * `method` (`bool`, optional): Whether to include a self parameter. Defaults
      to `True`.

    ### Returns:
    * `EventCallback`: decorated function
    """
    if method:
        def wrapper_method(self, control: ControlShadow, index: UnsafePluginIndex, *args: Any, **kwargs: Any) -> bool:
            # Filter button lifts
            if isinstance(control.getControl(), Button):
                if control.getCurrentValue() == 0.0:
                    return True
            return func(self, control, index, *args, **kwargs)
        return wrapper_method
    else:
        def wrapper(control: ControlShadow, index: UnsafePluginIndex, *args: Any, **kwargs: Any) -> bool:
            # Filter button lifts
            if isinstance(control.getControl(), Button):
                if control.getCurrentValue() == 0.0:
                    return True
            return func(control, index, *args, **kwargs)
        return wrapper
