import adsk.core
from ..helpers.misc import setUserParam

from ..lib import fusion360utils as futil
from ..helpers.store import loadVariable, storeVariable
import math

PSC_GROUP = "group"
PSC_MIN = "min"
PSC_MAX = "max"
PSC_PARAM = "param"

RESET_PARAM = "--zurücksetzen--"

def ceil(x):
    return int(math.ceil(x))

def floor(x):
    return int(math.floor(x))

class ParamSlider():
    
    def __init__(self,name,  inputTarget, parent):
        self.config = loadVariable(name, None, self._getConfigFileName())
        self.inputTarget = inputTarget
        self.name = name   
        self.parent = parent
        
        self.slider = None     
        self._setupConfig()        
        
        self.dirty = False
        
    def _getConfigFileName(self):
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        
        id = design.parentDocument.creationId
        
        fname = "sliders-%s.json" % id
        futil.log("Config File: %s" % fname)
        return fname
        
        
        
    def getParamName(self):
        return self.config['userParam']
 
    def _setupConfig(self):
        
        if self.config == None:
            self.config = {}
            
            self.config['min'] = 0       
            self.config['max'] = 1
            self.config['userParam'] = None
            
    def _getParams(self):
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        
        keys = []
        
        usedParams = self.parent.getUsedParamNames()
        
        for paramIndex in range(design.userParameters.count):
            param =  design.userParameters.item(paramIndex)
            
            if not param.name in usedParams or param.name == self.config['userParam']:            
                keys.append(param.name)        
        return keys
    
    def updateParamsList(self):
        self.paramDropdown.listItems.clear()
        
        for param in self._getParams():
            self.paramDropdown.listItems.add(param, self.config['userParam'] == param)
            
        self.paramDropdown.listItems.add(RESET_PARAM, False)
    
    def getUserParamValue(self, param):
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        currentValue = design.userParameters.itemByName(self.config['userParam'])
        
        if currentValue == None:
            return None
        else:
            return currentValue.value
    
    def _create(self):
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        
        label = None
        
        if self.config != None:
            label = self.config['userParam']
            pass
        
        if label == None:
            label = "Unbenannter Slider"
    
        
        
        # fix min max if necessary
        if self.config['userParam'] != None:
            currentValue = self.getUserParamValue(self.config['userParam'])
            
            if currentValue != None:
                futil.log("Current Value: %s" % currentValue)
                if self.config['min'] > int(currentValue):
                    self.config['min'] = int(currentValue)
                
                if self.config['max'] < int(currentValue):
                    self.config['max'] = int(currentValue)
                
        
        
        self.inputTarget.addTextBoxCommandInput(self.name + "_label",'', label , 1, True)       
        
        self.slider = self.inputTarget.addFloatSliderCommandInput(self.name, "Wert","", self.config['min'], self.config['max'], False)    
            
        if self.config['userParam'] != None:
                currentValue = design.userParameters.itemByName(self.config['userParam'])
                
                if currentValue != None:
                    futil.log("trying to set initial value to slider: %s" % currentValue.value)
                    if self.slider.maximumValue < currentValue.value:
                        self.slider.maximumValue = currentValue.value
                    self.slider.valueOne = currentValue.value
        
        
        self.settingsGroup = self.inputTarget.addGroupCommandInput(self.name + PSC_GROUP, 'Einstellungen')
        self.settingsGroup.isExpanded = False
        groupChildInputs = self.settingsGroup.children
        
        self.paramDropdown = groupChildInputs.addDropDownCommandInput(self.name + PSC_PARAM, 'Parameter', adsk.core.DropDownStyles.TextListDropDownStyle)
    
        self.updateParamsList()
    
        
        
        self.minInput = groupChildInputs.addIntegerSpinnerCommandInput(self.name+PSC_MIN, "Min",0,1000,1, self.config['min'] )
        self.maxInput = groupChildInputs.addIntegerSpinnerCommandInput(self.name+PSC_MAX, "Max",0,1000,1, self.config['max'] )
        
    
    def _storeConfig(self):
        storeVariable(self.name, self.config, self._getConfigFileName())
        
    
    def onChange(self, changed_input, inputs):
        param_id = changed_input.id
        
        
        
        
        if param_id.startswith(self.name) and param_id != self.name + PSC_GROUP:
            futil.log("paramSliderChange: %s" % param_id)
            
            min_slider = inputs.itemById(self.name + PSC_MIN)
            max_slider = inputs.itemById(self.name + PSC_MAX)
            self.slider = self.inputTarget.itemById(self.name)
            
            
            if param_id == self.name + PSC_MIN:
                            
                self.config['min'] = min_slider.value
                
            if param_id == self.name + PSC_MAX:
                
                self.config['max'] = max_slider.value
                
            if param_id == self.name + PSC_PARAM:     
                if changed_input.selectedItem.name == RESET_PARAM:
                    self.config['userParam'] = None
                    self.inputTarget.itemById(self.name + "_label").formattedText = "Unbenannter Slider"
                    self.slider.valueOne = 0.0
                    return
                
                           
                self.config['userParam'] = changed_input.selectedItem.name
                currentValue = self.getUserParamValue(changed_input.selectedItem.name)
                if currentValue != None:
                    if currentValue < 0:
                        min_slider.value = floor(currentValue * 2)
                        max_slider.value = ceil(currentValue * -2)
                    else:
                        min_slider.value = 0
                        newValue = ceil(currentValue * 2)
                        futil.log("trying to set  max_slider.value %s" % newValue)
                        max_slider.value = newValue
                    
                    self.slider.minimumValue = min_slider.value
                    self.slider.maximumValue = max_slider.value
                    self.inputTarget.itemById(self.name + "_label").formattedText = changed_input.selectedItem.name
                    
                    self.config['max'] = int(self.slider.maximumValue)
                    self.config['min'] = int(self.slider.minimumValue )
                    
                    futil.log("Trying to set value for slider: %s -> %s (%s , %s)" % (self.slider.valueOne, currentValue, self.slider.minimumValue, self.slider.maximumValue ))
                    self.slider.valueOne = currentValue
                    
                else:
                    futil.log("Could not get the latest value for %s" % changed_input.selectedItem.name)
                    
                # if the name was changed, we need to read the current param
                
                
            if param_id == self.name:
                # actual slider change
                self.dirty = True
                try:
                    #setUserParam(self.config['userParam'], self.slider.valueOne)
                    pass
                except:
                    futil.log("could not set slider value")
                    pass
            
                
    def onPreview(self):
        if self.config['userParam'] != None:
            try:
                setUserParam(self.config['userParam'], self.slider.valueOne)
                self.dirty = False
            except Exception as e:
                futil.log("cannot preview %s, because of %s" % (self.name, str(e)))
        pass
    
    def onExecute(self):
        self._storeConfig()
    
        
        try:
            setUserParam(self.config['userParam'], self.slider.valueOne)
        except:
            futil.log("cannot preview %s" % self.name)
        pass
    