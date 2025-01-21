import math
from .lib import fusionAddInUtils as futil
import adsk.core
import os
import adsk.fusion
import traceback
try:
    from .lib import qrcode as qrcode
except:
    import re
    import shutil
    CopyPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'qrcode')
    PastePath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(re.__cached__))), "site-packages", "qrcode")
    shutil.copytree(CopyPath, PastePath)
app = adsk.core.Application.get()
ui = app.userInterface
# TODO *** Specify the command identity information. ***
CMD_ID = "QR_Code"
CMD_NAME = 'QR Code'
CMD_Description = '' #Add a description of the add-in
IS_PROMOTED = True
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidCreatePanel'
COMMAND_BESIDE_ID = 'PrimitivePipe'
Size = 2.54
SelectedDefault = 0
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')


local_handlers = []
def run(context):
    try:
        cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
        futil.add_handler(cmd_def.commandCreated, command_created)
        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        panel = workspace.toolbarPanels.itemById(PANEL_ID)
        control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
        control.isPromoted = IS_PROMOTED
        #start()

    except:
        futil.handle_error('run')


def stop(context):
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()
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
        # This will run the start function in each of your commands as defined in commands/__init__.py
        #stop()

    except:
        futil.handle_error('stop')



def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs
    ShareLinkIcon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', "ShareLinkIcon", "")
    design: adsk.fusion.Design = app.activeProduct
    DropDown = inputs.addDropDownCommandInput("ShapeSelect", "Voxels", 1)
    DropDown.listItems.add("Square", False)
    DropDown.listItems.add("Cube", False)
    DropDown.listItems.add("Sphere", False)
    DropDown.listItems.add("Circle", False)
    DropDown.isFullWidth = False
    DropDown.listItems.item(SelectedDefault).isSelected = True
    try:
        if design.parentDocument.dataFile.versionNumber > 0:
            inputs.addBoolValueInput("ShareLink", "Share Link", False, ShareLinkIcon, False)
    except:
        pass
    TextEncode = inputs.addTextBoxCommandInput("Text", "Text To Encode", "", 1, False)
    
    #planeqty = inputs.addIntegerSpinnerCommandInput("PlaneQTY", "Number of Planes", 1, 100, 1, PlaneQTY)
    size = inputs.addValueInput("Size", "Size of voxels", "in", adsk.core.ValueInput.createByReal(Size))
    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')
    global Size
    

    inputs = args.command.commandInputs
    #BasePlaneSelecter: adsk.core.SelectionCommandInput = inputs.itemById("BasePlane")
    Text: adsk.core.TextBoxCommandInput = inputs.itemById("Text")
    size: adsk.core.ValueCommandInput = inputs.itemById("Size")
    ShapeChoice: adsk.core.DropDownCommandInput = inputs.itemById("ShapeSelect")

    CreateMatrix(Text.text, size.value, ShapeChoice.selectedItem.name)

    Size = size.value
    



# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    pass


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs
    Text = adsk.core.TextBoxCommandInput = inputs.itemById("Text")
   
    if inputs.itemById("ShareLink").value is True:
        design: adsk.fusion.Design = app.activeProduct
        ShareLink = design.parentDocument.dataFile.sharedLink
        ShareLink.isShared = True    
        Text.text = ShareLink.linkURL
    


    # General logging for debug.
    #futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    #futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values. This controls if the OK button is enabled or not.

        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []



def CreateMatrix(Text, Size, Voxels):
    Plane: adsk.fusion.ConstructionPlane
    ui = None
    global SelectedDefault
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design: adsk.fusion.Design = app.activeProduct         
        rootComp: adsk.fusion.Component = design.rootComponent  
        tempBrepMgr = adsk.fusion.TemporaryBRepManager.get()  
        QRComp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        QRComp.component.name = f"QR Code: {Text}"
        qr = qrcode.QRCode(box_size=1, border=0)
        qr.add_data(Text)
        qr.make(fit=True)
        qrMatrix = qr.get_matrix()
        CombineCollection = adsk.core.ObjectCollection.create()
        BoxSize = Size
        Start_x, Start_Y = 0,((len(qrMatrix)-1) * BoxSize)
        Number = 0
        TotalVoxels = len(qrMatrix)*2
        ui.progressBar.show("", 0, TotalVoxels, True)
        for row_idx, row in enumerate(qrMatrix):
            for col_idx, cell in enumerate(row):
                if cell == True:
                    x = Start_x + col_idx * BoxSize
                    y = Start_Y - row_idx * BoxSize
                    rect_points = [
                        adsk.core.Point3D.create(x, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y + BoxSize, 0),
                        adsk.core.Point3D.create(x, y + BoxSize, 0)
                    ]
                    CenterLine = adsk.core.Line3D.create(rect_points[0], rect_points[2])
                    (__, SP, EP) = CenterLine.evaluator.getParameterExtents()
                    (__, MP) = CenterLine.evaluator.getPointAtParameter((SP + EP) / 2)
                    LineLength = rect_points[0].vectorTo(rect_points[1])
                    LineWidth = rect_points[0].vectorTo(rect_points[3])
                    
                    if Voxels == "Square":
                        Box = CreateSquare(MP, BoxSize, LineLength, LineWidth)
                        SelectedDefault = 0
                    if Voxels == "Cube":
                        Box = CreateCube(MP, BoxSize, LineLength, LineWidth)
                        SelectedDefault = 1
                    if Voxels == "Sphere":
                        Box = CreateSphere(MP, BoxSize)
                        SelectedDefault = 2
                    if Voxels == "Circle":
                        Box = CreateCircle(MP, BoxSize)
                        SelectedDefault = 3

                    if CombineCollection.count > 0:
                        tempBrepMgr.booleanOperation(CombineCollection.item(0), Box, adsk.fusion.BooleanTypes.UnionBooleanType)
                    elif CombineCollection.count == 0:
                        CombineCollection.add(Box)
                    ui.progressBar.progressValue = Number
                    Number += 1
        ui.progressBar.hide()
        createdPixel = rootComp.bRepBodies.add(CombineCollection.item(0)) 
        MovedBody = createdPixel.moveToComponent(QRComp)
        MovedBody.isSelectable = False
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def CreateSquare(MP, BoxSize, LineLength, LineWidth):
    tempBrepMgr = adsk.fusion.TemporaryBRepManager.get()  
    orientedBoundBox = adsk.core.OrientedBoundingBox3D.create(MP, LineLength, LineWidth, BoxSize, BoxSize, 1)
    Square = tempBrepMgr.createBox(orientedBoundBox)
    return Square

def CreateCube(MP, BoxSize, LineLength, LineWidth):
    tempBrepMgr = adsk.fusion.TemporaryBRepManager.get()  
    orientedBoundBox = adsk.core.OrientedBoundingBox3D.create(MP, LineLength, LineWidth, BoxSize, BoxSize, BoxSize)
    Square = tempBrepMgr.createBox(orientedBoundBox)
    return Square

def CreateSphere(MP, BoxSize):
    tempBrepMgr = adsk.fusion.TemporaryBRepManager.get()  
    Sphere = tempBrepMgr.createSphere(MP, BoxSize/2)
    return Sphere


def CreateCircle(MP, BoxSize):
    MP: adsk.core.Point3D = adsk.core.Point3D.create(MP.x, MP.y, -0.5)
    tempBrepMgr = adsk.fusion.TemporaryBRepManager.get()
    P = adsk.core.Point3D.create(MP.x, MP.y, 0.5)
    Circle = tempBrepMgr.createCylinderOrCone(MP, BoxSize / 2.1, P, BoxSize / 2.1)
    return Circle
