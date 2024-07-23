


from .paramSlider import PSC_PARAM, ParamSlider
from ..lib import fusion360utils as futil
import adsk.core
from ..helpers.store import loadVariable, storeVariable

PSC_NUM_SLIDERS = "numSliders"

class ParamSliderGroup():
    
    def __init__(self, inputTarget, num_sliders = 4):
        self.inputTarget = inputTarget
        
        self.sliders = []
        
        numSlidersDb = loadVariable(PSC_NUM_SLIDERS, num_sliders, self._getConfigFileName())
        self.num_sliders = numSlidersDb
        
        for x in range(numSlidersDb):
            self.sliders.append(ParamSlider("param_slider_%s" % x, self.inputTarget, self))
            
        for s in self.sliders:
            s._create()
            
        self.inputTarget.addIntegerSpinnerCommandInput(PSC_NUM_SLIDERS, "Anzahl Slider",0,20,1, self.num_sliders )
        
        
        
    
    def _getConfigFileName(self):
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        
        id = design.parentDocument.creationId
        
        fname = "sliders-%s.json" % id
        futil.log("Config File: %s" % fname)
        return fname
    
    def onExecute(self):
        for x in self.sliders:  
            x.onExecute()

    def onPreview(self):
        for x in self.sliders:  
            x.onPreview()
            
    def onChange(self, changed_input, inputs):
        if changed_input.id == PSC_NUM_SLIDERS:
            futil.log(str(changed_input.value))
            storeVariable(PSC_NUM_SLIDERS, changed_input.value, self._getConfigFileName())
            #loadVariable(PSC_NUM_SLIDERS, num_sliders, self._getConfigFileName())
            return
        
        
        for ps in self.sliders:
            ps.onChange(changed_input, inputs)
            
        if changed_input.id.endswith(PSC_PARAM):
            futil.log("updating dropdowns")
            for ps in self.sliders:
                pass
                #ps.updateParamsList()
    
    
    def getUsedParamNames(self):
        names = []
        
        for ps in self.sliders:
            names.append(ps.getParamName())
        
        return list(set(names))