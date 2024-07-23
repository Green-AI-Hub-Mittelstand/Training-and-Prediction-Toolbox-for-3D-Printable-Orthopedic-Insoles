
import adsk.core
import os

from ...helpers.misc import setUserParam

from ...helpers.paramSlider import ParamSlider
from ...helpers.paramSliderGroup import ParamSliderGroup

from ...helpers.versions import get_last_commit_date, git_pull

from ...helpers.foamPoints import FoamPointDefinitions, InsolePoint, getPointByType

from ...helpers.requests import getApiEndpoint, getCustomers, getInsole, getInsoles, getParticipantInsole, getParticipants

from ...helpers.constants import *

from ...helpers.store import loadVariable, storeVariable
from ...lib import fusion360utils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Einlagen Parameter2'
CMD_Description = 'A Fusion 360 Add-in Command with a dialog'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []

design = adsk.fusion.Design.cast(app.activeProduct)


paramSliders = None

thereWasUserInput = False


#INPUT_API_URL = "api_url"

selectedParams = None
selectedInsoleData = None
selectedParticipantData = None
selectedFoot = None

participantLink = None
gitVersion = None


input_selected_customer = None
input_selected_customer_insole = None
input_selected_participant = None
input_selected_foot = None

# Executed when add-in is run.
def start():
    
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


insoleDropdownCustomer = None

customerTab = None
participantTab = None
paramsTab = None
settingsTab = None

paramsDropdown  = None
paramsSliderTab = None
footDropdown = None


def loadParamEntries():
    global paramsTab, paramsDropdown
    
    paramentries = loadVariable(INPUT_PARAMS,[],FN_USER_PARAMS)
    
    paramsDropdownItems = paramsDropdown.listItems
    paramsDropdownItems.clear()
    
    
    
    lastParams = loadVariable(INPUT_PARAMS,None)
    for p in paramentries:
        label  = p['date-time']
        paramsDropdownItems.add(label, lastParams==label)
    


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    global insoleDropdownCustomer, customerTab, participantTab, settingsTab, paramsTab, paramsDropdown, participantLink, gitVersion, paramsSliderTab, paramSliders, footDropdown, thereWasUserInput
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created 2 Event')
    
    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs
    
    args.command.setDialogMinimumSize(250, 150)

    loadingProgress = showProgress(6,"Lade Daten vom Server..")

    ############# TABS
    customerTab = inputs.addTabCommandInput('tab_1', 'Kunden')
    tab1ChildInputs = customerTab.children
    
    participantTab = inputs.addTabCommandInput('tab_2', 'Probanden')
    tab2ChildInputs = participantTab.children
    
    settingsTab = inputs.addTabCommandInput('tab_3', 'Einstellungen')
    tab3ChildInputs = settingsTab.children
    
    paramsTab = inputs.addTabCommandInput('tab_4', 'Parameter')
    paramsTabChildInputs = paramsTab.children
    
    paramsSliderTab = inputs.addTabCommandInput('tab_5', 'Slider')
    paramsSliderTabChildInputs = paramsSliderTab.children
    
    tabs = [customerTab, participantTab, settingsTab,paramsTab, paramsSliderTab]
    
    lastTab = loadVariable(INPUT_TAB, None)
    if lastTab != None:
        for i, tab in enumerate(tabs):
            if i == lastTab:
                tab.activate()
                
                
    ############# END TABS
    
    ###### TAB 5 Params Slider
    paramSliders = ParamSliderGroup(paramsSliderTabChildInputs, 4)
    
    
    
    
    ###### TAB 4 Params
    
    paramsDropdown = paramsTabChildInputs.addDropDownCommandInput(INPUT_PARAMS, 'Parameter', adsk.core.DropDownStyles.TextListDropDownStyle)
    loadParamEntries()
    loadingProgress.progressValue +=1
        
    paramsTabChildInputs.addBoolValueInput(INPUT_STORE_PARAMS, "Nutzerparameter speichern", False, '')
    paramsTabChildInputs.addBoolValueInput(INPUT_DELETE_PARAMS, "ausgewähltes Set löschen", False, '')
    
    
    ###### TAB 1 - Kunden
    customers = getCustomers()
    loadingProgress.progressValue +=1
    customerDropdown = tab1ChildInputs.addDropDownCommandInput(INPUT_CUSTOMER, 'Kunde', adsk.core.DropDownStyles.TextListDropDownStyle)
    customerDropdownItems = customerDropdown.listItems
    
    
    lastCustomer = loadVariable(INPUT_CUSTOMER,None)
    for c in customers:            
        label = "[%s] %s, %s" % (c['id'], c['last_name'], c['first_name'])
        customerDropdownItems.add(label, lastCustomer==label)
        
        
    insoleDropdownCustomer = tab1ChildInputs.addDropDownCommandInput(INPUT_INSOLE_CUSTOMER, 'Einlage', adsk.core.DropDownStyles.TextListDropDownStyle)
    
    if lastCustomer != None:
        onCustomerChanged(lastCustomer)
        loadingProgress.progressValue +=1
    
    
    ###### TAB 2 - Probanden
    participants = getParticipants()
    loadingProgress.progressValue +=1
    participantDropdown = tab2ChildInputs.addDropDownCommandInput(INPUT_PARTICIPANT, 'Proband', adsk.core.DropDownStyles.TextListDropDownStyle)
    participantDropdownItems = participantDropdown.listItems
    
    lastParticipant = loadVariable(INPUT_PARTICIPANT)
    for c in participants:            
        label = "[%s] %s (%s)" % (c['public_id'],c['created'], c['shoe_size'])
        participantDropdownItems.add(label, lastParticipant==label)
        
        
    message = '<div align="center">-</div>'
    participantLink =  tab2ChildInputs.addTextBoxCommandInput('fullWidth_textBox', '', message, 1, True)       
        
    if lastParticipant != None:
        onParticipantChanged(lastParticipant)
        loadingProgress.progressValue +=1
        
    #participantDropdown = tab1ChildInputs.addDropDownCommandInput(INPUT_INSOLE_CUSTOMER, 'Einlage', adsk.core.DropDownStyles.TextListDropDownStyle)
    
    
    
    ###### TAB 3 - Einstellungen
    api_endpoint = loadVariable(INPUT_API_URL, "http://127.0.0.1:8000/api")
    api_token = loadVariable(INPUT_API_TOKEN, "xx")
    api_secret = loadVariable(INPUT_API_SECRET, "xx")
    
    tab3ChildInputs.addTextBoxCommandInput(INPUT_API_URL, 'API URL', api_endpoint, 1, False)
    tab3ChildInputs.addTextBoxCommandInput(INPUT_API_TOKEN, 'Token', api_token, 1, False)
    tab3ChildInputs.addTextBoxCommandInput(INPUT_API_SECRET, 'Secret', api_secret, 1, False)
    
    
    
    gitVersion = tab3ChildInputs.addTextBoxCommandInput('git_date','',"",1,True)
    tab3ChildInputs.addBoolValueInput(INPUT_GET_ADDIN_VERSION, "Version abfragen", False, '')
    tab3ChildInputs.addBoolValueInput(INPUT_UPDATE_ADDIN, "Addin aktualisieren", False, '')
    
    
    
    ## GENERAL
    footDropdown = inputs.addDropDownCommandInput(INPUT_FOOT, 'Fuß', adsk.core.DropDownStyles.TextListDropDownStyle)
    
    onTabChange()
    
    
    lastFoot = loadVariable(INPUT_FOOT, None)
    
    
    footDropdown.listItems.add(VALUE_left,lastFoot==VALUE_left)
    footDropdown.listItems.add(VALUE_right,lastFoot==VALUE_right)
    
    if lastFoot != None:
        onFootChange(lastFoot)
        loadingProgress.progressValue +=1
    
    
    
    #inputs.addBoolValueInput(INPUT_LOAD_PARAMS, 'Parameter laden', False)
    
    loadingProgress.hide()
    

    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def onUserParamsLoad():
    global paramsTab, selectedParams
    
    design = adsk.fusion.Design.cast(app.activeProduct)
    
    paramentries = loadVariable(INPUT_PARAMS,[],FN_USER_PARAMS)
    
    for p in paramentries:
        if p ['date-time'] == selectedParams:
            progress = showProgress(len(p['params']))
            
            for i, p_key in enumerate(p['params']):
                currentValue = design.userParameters.itemByName(p_key)
                
                if currentValue != None:
                    currentValue.expression = p['params'][p_key]
                else:
                    futil.log("could not find user parameter %s" % p_key)
            
                progress.progressValue = i+1
                
    progress.hide()

# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    global customerTab, participantTab, settingsTab, paramsTab, paramsSliderTab, thereWasUserInput
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    thereWasUserInput = False
    

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    
    input_api_endpoint = adsk.core.TextBoxCommandInput = inputs.itemById(INPUT_API_URL)
    input_api_token = adsk.core.TextBoxCommandInput = inputs.itemById(INPUT_API_TOKEN)
    input_api_secret = adsk.core.TextBoxCommandInput = inputs.itemById(INPUT_API_SECRET)
    
    storeVariable(INPUT_API_URL, input_api_endpoint.text)
    storeVariable(INPUT_API_TOKEN, input_api_token.text)
    storeVariable(INPUT_API_SECRET, input_api_secret.text)
    
    
    
    
    if customerTab.isActive or participantTab.isActive:    
        onLoadClicked() 
        storeVariable(INPUT_FOOT, input_selected_foot)
        return
    
    if customerTab.isActive:
        storeVariable(INPUT_CUSTOMER, input_selected_customer)
        storeVariable(INPUT_INSOLE_CUSTOMER, input_selected_customer_insole)
        
        
    if participantTab.isActive:
        storeVariable(INPUT_PARTICIPANT, input_selected_participant)
        
    
    if paramsTab.isActive:
        onUserParamsLoad()
        
        
        
    if paramsSliderTab.isActive:
        paramSliders.onExecute()
            
    
    #ui.messageBox(msg)
    
    #ui.messageBox("Fertig")
    



# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    global thereWasUserInput
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    
    if paramsSliderTab.isActive:    
        paramSliders.onPreview()
        
    if participantTab.isActive:
        futil.log("Preview for the participant tab")
        if thereWasUserInput:
            onLoadClicked() 
            args.isValidResult = True
            
    if customerTab.isActive:
        futil.log("Preview for the customer tab")
        if thereWasUserInput:
            onLoadClicked() 
            args.isValidResult = True
        


import re

def getIdFromListItemText(text):
    # Define the pattern
    pattern = r"\[(\w+)\]"

    # Search for the pattern in the string
    match = re.search(pattern, text)

    if match:
        # Extract the xx part
        xx_part = match.group(1)
        return xx_part
    else:
        return False

def onCustomerChanged(customer_entry):
    global insoleDropdownCustomer, input_selected_customer
    
    input_selected_customer = customer_entry
    storeVariable(INPUT_CUSTOMER, customer_entry)
    futil.log("selected customer: %s ---- %s" % (customer_entry, getIdFromListItemText(customer_entry)))
    
    customer_id =getIdFromListItemText(customer_entry)
    
    insoles = getInsoles(customer_id)
    
    insoleDropdownCustomer.listItems.clear()
    
    lastInsole = None
    #lastInsole = loadVariable(INPUT_INSOLE_CUSTOMER, None)
    
    for insole in insoles:
        label = "[%s] %s " % (insole["id"], insole['created'])
        insoleDropdownCustomer.listItems.add(label, label == lastInsole)
        
    if lastInsole != None:
        onCustomerInsoleChanged(lastInsole)




def onCustomerInsoleChanged(insole_entry):
    global selectedInsoleData, input_selected_customer_insole
    
    input_selected_customer_insole = insole_entry
    insole_id = getIdFromListItemText(insole_entry)    
    
    try:
        selectedInsoleData = getInsole(insole_id)
    except Exception as e:
        futil.log("Could not load insole for customer")
        futil.log(str(e))
        raise e
    else:
        storeVariable(INPUT_INSOLE_CUSTOMER, insole_entry)
        
        # ohoh
        #onLoadClicked() 
    
    
    
def onFootChange(foot_entry):
    global selectedFoot, input_selected_foot
    selectedFoot = foot_entry
    input_selected_foot = selectedFoot
    
    storeVariable(INPUT_FOOT, foot_entry)
    pass

def onParticipantChanged(participant_entry):
    global selectedParticipantData, addTextBoxCommandInput, input_selected_participant
    
    input_selected_participant = participant_entry
    
    participant_public_id = getIdFromListItemText(participant_entry)
    
    
    # request data
    try:
        selectedParticipantData = getParticipantInsole(participant_public_id)
    except:
        futil.log("could not load participant insole")
    else:
        
        
        dbId = selectedParticipantData['participant']['id']
        
        api_endpoint = getApiEndpoint().replace("api/","").replace("api","")
        
        api_endpoint += "inspect/inspectParticipant/%s/"  % (dbId,)
        
        
        
        participantLink.formattedText = "<div align='center'><a href='%s'>Schaumabdruck ansehen</a></div>" % api_endpoint
        
        
        
    

from datetime import datetime
def now():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y %H:%M:%S")
    
    return formatted_datetime

def onDeleteParams():
    global selectedParams
    
    if selectedParams == None or selectedParams == -1:
        ui.messageBox("Keine Parameter ausgewählt")
        return
    
    returnValue = ui.messageBox("Parameter von %s wirklich löschen?"  % selectedParams, "Wirklich?",  3)
    
    if returnValue != 2:    
        return

    
    
    paramentries = loadVariable(INPUT_PARAMS,[],FN_USER_PARAMS)
    
    newParamentries = []
    
    for p in paramentries:
        if p['date-time'] != selectedParams:
            newParamentries.append(p)
    
    storeVariable(INPUT_PARAMS, newParamentries,FN_USER_PARAMS)
    
    
    
    selectedParams = None    
    storeVariable(INPUT_PARAMS,"-1")
    loadParamEntries()
    
    ui.messageBox("gelöscht.")
    pass
   
def onStoreParams():
    global selectedParams
    design = adsk.fusion.Design.cast(app.activeProduct)
    
    
    
    params = {}
    
    for paramIndex in range(design.userParameters.count):
        param =  design.userParameters.item(paramIndex)
        futil.log("%s -> %s" % (param.name, param.expression))
        
        params[param.name] = param.expression
        
    # load the current set of params
    paramentries = loadVariable(INPUT_PARAMS,[],FN_USER_PARAMS)
    
    entry = {
        'date-time':now(),
        'params':params
    }
    
    paramentries.append(entry)
    storeVariable(INPUT_PARAMS, paramentries,FN_USER_PARAMS)
    
    selectedParams = entry['date-time']
    storeVariable(INPUT_PARAMS,selectedParams)
    
    loadParamEntries()
    ui.messageBox("gespeichert als '%s' " % selectedParams)
    
    

        

def showProgress(steps, title = 'Setze Parameter'):
    progressDialog = ui.createProgressDialog()
    progressDialog.isBackgroundTranslucent = False
    progressDialog.isCancelButtonShown = False
    progressDialog.show(title, 'Fortschritt: %p', 0, steps, 0)
    
    return progressDialog
        
    


def setParameters(params):
    design = adsk.fusion.Design.cast(app.activeProduct)
    # generate or set the parameters
    ignore_params = ['id','insole','comments','points','fersensporn','foot']
    
    paramPrefix = "AI_"
    
    progress = showProgress(len(params))
    
    
    for i, param in enumerate(params):
        param_value = params[param]
        
        paramName = paramPrefix + param
        
        if not param in ignore_params:
            futil.log("outer call %s" % param)
            setUserParam(paramName, param_value)
            
        
        progress.progressValue = i+1
    adsk.doEvents()
    progress.hide()
            
import time   


     
            
def setPoints(params):
    points = params['points']
    
    insolePoints = []
    for p  in points:
        insolePoints.append(InsolePoint(p['x'], p['y'], p['pointType']))
    
    bottomPoint = getPointByType(FoamPointDefinitions.HINTERSTER_PUNKT, insolePoints)
    schnittAchsePoint = getPointByType(FoamPointDefinitions.SCHNITTACHSE, insolePoints)
    
    progress= showProgress(len(insolePoints))
    
    futil.log(str(bottomPoint))
    futil.log(str(schnittAchsePoint))
    
    for i,p in enumerate(insolePoints):
        p.setCoordinatesOnAxis(bottomPoint, schnittAchsePoint)
        futil.log(str(p))
    
    
    # now update all points regarding the axis
    for i,p in enumerate(insolePoints):
        #p.setCoordinatesOnAxis(bottomPoint, schnittAchsePoint)
        
        #time.sleep(1)

        if not "Mittel" in p.label() or True:
        
            # and set the user parameters
            setUserParam("AI_p_"+p.label()+"_x", p.x_dist)
            setUserParam("AI_p_"+p.label()+"_y", p.y_dist)
            setUserParam("AI_p_"+p.label()+"_side", p.side)
            
        else:
            futil.log("Not setting %s -> %s" % (str(p), p.label()))
            
        progress.progressValue = i+1
    
    adsk.doEvents()
    progress.hide()
    
def drawTextSketch(tuple_list= []):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    
    ki_params_sketch = rootComp.sketches.itemByName("KI Parameter")
    
    texts = ki_params_sketch.sketchTexts 
    
    # delete all texts
    for i in range(texts.count):
        texts.item(i).deleteMe()
        

    pos_x = -20
    pos_y = 25
    
    # compile the text
    s = ""
    for (k, v) in tuple_list:
        s+="%s: %s \n" % (k,v)
    
    # write a new text
    input = texts.createInput2(s, 0.5)
    input.setAsMultiLine(adsk.core.Point3D.create(pos_x, pos_y, 0),
                             adsk.core.Point3D.create(pos_x+10, pos_y+8, 0),
                             adsk.core.HorizontalAlignments.LeftHorizontalAlignment,
                             adsk.core.VerticalAlignments.TopVerticalAlignment, 0)
    
    texts.add(input)
    




def onLoadClicked():
    global selectedFoot, selectedInsoleData
    
    #setUserParam("AI_foot", selectedFoot)
    
    
    
    
    if customerTab.isActive and selectedInsoleData != None and selectedFoot != None:
        
    
        msg = "insole id: %s, foot: %s" % (selectedInsoleData['id'], selectedFoot)
        #ui.messageBox(msg)
        
        # get left or right
        params = None
        
        if selectedFoot == VALUE_left:
            params = selectedInsoleData["leftParameters"]
        else:
            params = selectedInsoleData["rightParameters"]
            
        
        
        
        setParameters(params)        
        setPoints(params)
        
        
        #setUserParam("AI_foot", selectedFoot)
        
        
        
        
        return

    if participantTab.isActive and selectedParticipantData != None and selectedFoot != None:
        if selectedFoot == VALUE_left:
            params = selectedParticipantData["leftParameters"]
        else:
            params = selectedParticipantData["rightParameters"]
            
        setParameters(params)
        setPoints(params)
        
        drawTextSketch([
            ("Fuß",selectedFoot),
            ("Teilnehmer ID", selectedParticipantData['participant']['public_id']),
            ("Schuhgröße", selectedParticipantData['participant']['shoe_size']),
            ("Gewicht", selectedParticipantData['participant']['weight']),
            ("Größe", selectedParticipantData['participant']['height']),
            ("",""),
            ("Länger der E", params['laenge_der_einlage'])
            
        ])
        

def onTabChange():
    
    global customerTab, participantTab, settingsTab, paramsTab, paramsSliderTab
    
    tabs = [customerTab, participantTab, settingsTab, paramsTab, paramsSliderTab]
    
    index = 0
    for i, tab in enumerate(tabs):
        futil.log("testing tab %s" % i)
        
        
        if tab.isActive:
            index = i
            
            footDropdown.isVisible = tab.id in [customerTab.id, participantTab.id]
            
            
            
                
            
    
            
    storeVariable(INPUT_TAB,index)

def updateAddin():
    global gitVersion
    
    updateProgress = showProgress(3,"Addin Update...")
    
    last_date = get_last_commit_date()
    
    if last_date == None:
        updateProgress.hide()
        ui.messageBox("Das ging leider nicht..")
        return
    
    updateProgress.progressValue +=1
        
    git_pull()
    updateProgress.progressValue +=1
    updated_version = get_last_commit_date()
    updateProgress.progressValue +=1
    
    
    if last_date != updated_version:
        ui.messageBox("Neue Version!")
    else:
        ui.messageBox("Schon aktuell")
        
    
        
    gitVersion.formattedText = "Version: <b>%s</b>" % updated_version 
    
    updateProgress.hide()



    


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    global insoleDropdownCustomer, selectedParams, gitVersion, paramSliders, thereWasUserInput
    
    changed_input = args.input
    inputs = args.inputs
    
    
    
    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')

    
    if changed_input.id == INPUT_CUSTOMER:
        futil.log("from customer")
        thereWasUserInput = True
        onCustomerChanged(changed_input.selectedItem.name)
        
    
        return
        
        
    if changed_input.id == INPUT_INSOLE_CUSTOMER:
        futil.log("from insole")
        thereWasUserInput = True
        onCustomerInsoleChanged(changed_input.selectedItem.name)
        return
    
    if changed_input.id == INPUT_PARTICIPANT:
        futil.log("from insole")
        thereWasUserInput = True
        onParticipantChanged(changed_input.selectedItem.name)
        return
    
        
    if changed_input.id == INPUT_FOOT:
        futil.log("from INPUT_FOOT")
        thereWasUserInput = True
        onFootChange(changed_input.selectedItem.name)    
        return

    if changed_input.id == INPUT_LOAD_PARAMS:
        futil.log("from INPUT_LOAD_PARAMS")
        return
        
    if changed_input.id == "APITabBar":
        onTabChange()
        return
        
    if changed_input.id == INPUT_STORE_PARAMS:
        onStoreParams()
        return
        
    if changed_input.id == INPUT_DELETE_PARAMS:
        onDeleteParams()
        return 
        
    if changed_input.id == INPUT_PARAMS:
        selectedParams = changed_input.selectedItem.name
        return 
        
    if changed_input.id == INPUT_GET_ADDIN_VERSION:
        last_date = get_last_commit_date()
        gitVersion.formattedText = "Version: <b>%s</b>" % last_date
        return
        
    if changed_input.id == INPUT_UPDATE_ADDIN:
        updateAddin()
        return
        
    paramSliders.onChange(changed_input, inputs)
        #   

    

# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    #futil.log(f'{CMD_NAME} Validate Input Event')
    global selectedFoot, selectedInsoleData, customerTab, participantTab, paramsTab, selectedParams, paramsSliderTab
    
    args.areInputsValid = False
    
    
    if customerTab.isActive:
        #futil.log("customerTab is active")
        val = selectedInsoleData != None and selectedFoot != None    
        args.areInputsValid = val
    
    if participantTab.isActive:
        #futil.log("participantTab is active")
        val = selectedParticipantData != None and selectedFoot != None    
        #futil.log(str(val))
        args.areInputsValid = val
        
    if settingsTab.isActive:
        args.areInputsValid = True
    
    if paramsTab.isActive and selectedParams != None and selectedParams != -1:
        args.areInputsValid = True
        
    if paramsSliderTab.isActive:
        args.areInputsValid = True
    
    
    #futil.log("Validate: %s" % val)
    
    
    
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    global thereWasUserInput
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')
    thereWasUserInput = False

    global local_handlers
    local_handlers = []
