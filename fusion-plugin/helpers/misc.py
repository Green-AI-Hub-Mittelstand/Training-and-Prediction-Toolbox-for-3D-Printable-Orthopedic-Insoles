def add_slash_if_needed(string):
    """
    Add a '/' to the end of the string if it does not already end with it.
    
    Parameters:
        string (str): The input string.
        
    Returns:
        str: The string with a '/' added at the end if necessary.
    """
    if not string.endswith('/'):
        return string + '/'
    else:
        return string

import adsk.core
from ..lib import fusion360utils as futil


def setUserParam(key, value):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    currentValue = design.userParameters.itemByName(key)
            
    futil.log("Trying to set param '%s': '%s'" % (key, value ))
    
    """
    value = 0
    try:
        value = float(value)
    except:
        value = 0
        futil.log("could not do that :(")    
    """
    
    
    paramValueInput = adsk.core.ValueInput.createByReal(float(value))
    
    if currentValue == None:
        # create it
        futil.log("Trying to add: '%s'" % (paramValueInput.realValue, ))
        
        ret = design.userParameters.add(key,paramValueInput,"","")
        
        if ret == None:
            futil.log("NOPE :(")
    else:
        # set it
        futil.log("Trying to set")
        currentValue.value = float(value)
        #design.userParameters.add(paramPrefix + param,param_value,"")
        
    