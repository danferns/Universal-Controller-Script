"""
bootstrap > util

Contains utility functions used within the rest of the code
"""

from typing import Any
from copy import deepcopy

def recursiveMergeDictionaries(ref: dict, override: dict, path:str='') -> dict:
    """
    Merge the contents of two nested dictionaries, ensuring all values in second
    override existing values in the first

    ### Args:
    * `ref` (`dict`): reference dictionary
    * `override` (`dict`): override dictionary
    * `path` (`str`, optional): path of current setting, used to give meaningful
      exception info. Defaults to ''.

    ### Returns:
    * `dict`: new dictionary representing the merged results
    """
    ERROR_HEADER = "Unable to load settings"
    # Get a copy of the dictionary
    # Note that a deep copy isn't necessary as nested contents will be copied
    # when we recurse, effectively making a manual deep copy
    new = ref.copy()
    
    for key, value in override.items():
        # Check for invalid settings value
        key_path = path + '.' + key
        if key not in ref:
            raise KeyError(f"{ERROR_HEADER}: {key_path} is "
                           f"not a valid settings value")
        ref_value = ref[key]
        
        # If it's a dictionary, we should recurse and copy those settings
        ## Using `type(x) is dict` so that a different inherited type can be used
        ## to specify when an actual settings value is of type dictionary
        if type(ref_value) is dict:
            # But first, make sure that we're given the correct type of setting
            if type(value) is not dict:
                raise TypeError(f"{ERROR_HEADER}: expected a category at "
                                f"{key_path}, not a value")
            # Recurse and merge the result
            new[key] = recursiveMergeDictionaries(ref_value, value, key_path)
        
        # Otherwise, we should set the value directly, by creating a copy
        else:
            # Make sure that we're using the correct type for the setting
            ## Check that the reference value is an instance of the type of the
            ## actual value. This ensures that if we have a settings value that
            ## is literally a dictionary, it won't cause it to fail when the
            ## user uses the simple `dict` type.
            if not isinstance(ref_value, type(value)):
                raise TypeError(f"{ERROR_HEADER}: expected a value of type "
                                f"{type(ref_value)} for settings value at "
                                f"{key_path}")
            new[key] = deepcopy(value)
    
    # Finally return the new dictionary
    return new

def dictKeyRecursiveInsert(d: dict, keys: list[str], val: Any, key_full: str) -> None:
    """
    Insert a value at the location of a nested key, adding new dictionaries as
    required

    ### Args:
    * `d` (`dict`): dictionary to add to
    * `keys` (`list[str]`): keys to recurse to
    * `val` (any): value to insert
    * `key_full` (`str`): path to key, for use in exceptions
    """
    if len(keys) == 1:
        if keys[0] in d:
            raise KeyError(f"Duplicate key at {key_full}")
        d[keys[0]] = val
        return
    if keys[0] not in d:
        d[keys[0]] = {}
    dictKeyRecursiveInsert(d[keys[0]], keys[1:], val, key_full)

def expandDictShorthand(d: dict[str, Any], path:str='') -> dict:
    """
    Recursively expands short-hand notation for dictionary data

    For example,
    ```py
    {
        "foo.bar": 1,
        "foo.baz": 2,
        "bat: 3
    }
    ```
    would expand to
    ```py
    {
        "foo": {
            "bar": 1,
            "baz"2
        },
        "bat": 3
    }
    ```

    ### Args:
    * `d` (`dict`): dictionary to expand
    * `path` (`str`, optional): path string to give meaningful exceptions.\
      Defaults to ''.

    ### Returns:
    * `dict`: new dictionary that is expanded
    """
    new = {}
    
    for key, value in d.items():
        full_key = path + '.' + key
        # If it's a dict, make sure it is expanded as well
        if isinstance(value, dict):
            value = expandDictShorthand(value, full_key)
        # Expand the path and insert it in the correct location
        split_path = key.split('.')
        dictKeyRecursiveInsert(new, split_path, value, full_key)
        
    return new