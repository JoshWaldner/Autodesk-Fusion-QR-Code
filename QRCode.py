import math
from .lib import fusionAddInUtils as futil
import adsk.core
from .lib import qrcode as qrcode
#import qrcode as qrcode
import os
import adsk.fusion
import traceback
#from . import config
app = adsk.core.Application.get()
ui = app.userInterface
# TODO *** Specify the command identity information. ***
CMD_ID = "TaraCon_QR_Code"
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
    global SelectedDefault

    inputs = args.command.commandInputs
    #BasePlaneSelecter: adsk.core.SelectionCommandInput = inputs.itemById("BasePlane")
    Text: adsk.core.TextBoxCommandInput = inputs.itemById("Text")
    size: adsk.core.ValueCommandInput = inputs.itemById("Size")
    ShapeChoice: adsk.core.DropDownCommandInput = inputs.itemById("ShapeSelect")

    if ShapeChoice.selectedItem.name == "Square":
        SquarePixels(Text.text, size.value)
        SelectedDefault = 0
    elif ShapeChoice.selectedItem.name == "Cube":
        CubePixels(Text.text, size.value)
        SelectedDefault = 1
    elif ShapeChoice.selectedItem.name == "Sphere":
        SpherePixels(Text.text, size.value)
        SelectedDefault = 2
    elif ShapeChoice.selectedItem.name == "Circle":
        CirclePixels(Text.text, size.value)
        SelectedDefault = 3
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

def InsertCommand(RootComp, Command: str):
    sels = ui.activeSelections
    sels.clear()
    sels.add(RootComp)
    app.executeTextCommand("Commands.Start " + Command)
    sels.clear()

def SquarePixels(Text, Size):
    Plane: adsk.fusion.ConstructionPlane
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design: adsk.fusion.Design = app.activeProduct         
        rootComp: adsk.fusion.Component = design.rootComponent    
        QRComp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        QRComp.component.name = f"QR Code: {Text}"
        qr = qrcode.QRCode(box_size=1, border=0)
        qr.add_data(Text)
        qr.make(fit=True)
        qrMatrix = qr.get_matrix()
        CombineCollection = adsk.core.ObjectCollection.create()
        ExtrudeCollection = adsk.core.ObjectCollection.create()
        progressDialog = ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.isCancelButtonShown = True
        True_Count = sum(row.count(True) for row in qrMatrix)
        progressDialog.show('Progress Dialog', f"%p% Completed\n%v of %m", 0, True_Count)
        PixelCount = 1
        BoxSize = Size
        Start_x, Start_Y = 0,0
        for row_idx, row in enumerate(qrMatrix):
            if progressDialog.wasCancelled:
                break
            for col_idx, cell in enumerate(row):
                if progressDialog.wasCancelled:
                    break
                if cell == True:
                    x = Start_x + col_idx * BoxSize
                    y = Start_Y + row_idx * BoxSize
                    rect_points = [
                        adsk.core.Point3D.create(x, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y + BoxSize, 0),
                        adsk.core.Point3D.create(x, y + BoxSize, 0)
                    ]
                    QRSketch = rootComp.sketches.addWithoutEdges(rootComp.xYConstructionPlane)
                    Square = QRSketch.sketchCurves.sketchLines.addTwoPointRectangle(rect_points[0], rect_points[2]) 
                    Profile = QRSketch.profiles.item(0)
                    ExtrudeCollection.add(Profile)
                    extrude = rootComp.features.extrudeFeatures                    
                    Distance = adsk.core.ValueInput.createByReal(1)
                    ExtrudeBody = extrude.addSimple(Profile, Distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    createdPixel = ExtrudeBody.bodies.item(0)
                    createdPixel.isSelectable = False
                    MovedPixel = createdPixel.moveToComponent(QRComp)
                    CombineCollection.add(MovedPixel)
                    QRSketch.deleteMe()
                    Feature = QRComp.component.features.item(0)
                    Feature.dissolve()
                    progressDialog.progressValue = PixelCount
                    PixelCount += 1
        progressDialog.hide()
        Combine = QRComp.component.features.combineFeatures
        Combine.createInput(QRComp.bRepBodies.item(0), CombineCollection)
        CombineCollection.removeByIndex(0)
        input: adsk.fusion.CombineFeatureInput = Combine.createInput(QRComp.bRepBodies.item(0), CombineCollection)
        input.isNewComponent = False
        input.isKeepToolBodies = False
        input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combineFeature = Combine.add(input)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def CubePixels(Text, Size):
    Plane: adsk.fusion.ConstructionPlane
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design: adsk.fusion.Design = app.activeProduct         
        rootComp: adsk.fusion.Component = design.rootComponent    
        QRComp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        QRComp.component.name = f"QR Code: {Text}"
        qr = qrcode.QRCode(box_size=1, border=0)
        qr.add_data(Text)
        qr.make(fit=True)
        qrMatrix = qr.get_matrix()
        CombineCollection = adsk.core.ObjectCollection.create()
        ExtrudeCollection = adsk.core.ObjectCollection.create()
        progressDialog = ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.isCancelButtonShown = True
        True_Count = sum(row.count(True) for row in qrMatrix)
        progressDialog.show('Progress Dialog', f"%p% Completed\n%v of %m", 0, True_Count)
        PixelCount = 1
        BoxSize = Size
        Start_x, Start_Y = 0,0
        for row_idx, row in enumerate(qrMatrix):
            if progressDialog.wasCancelled:
                break
            for col_idx, cell in enumerate(row):
                if progressDialog.wasCancelled:
                    break
                if cell == True:
                    x = Start_x + col_idx * BoxSize
                    y = Start_Y + row_idx * BoxSize
                    rect_points = [
                        adsk.core.Point3D.create(x, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y + BoxSize, 0),
                        adsk.core.Point3D.create(x, y + BoxSize, 0)
                    ]
                    QRSketch = rootComp.sketches.addWithoutEdges(rootComp.xYConstructionPlane)
                    Square = QRSketch.sketchCurves.sketchLines.addTwoPointRectangle(rect_points[0], rect_points[2]) 
                    Profile = QRSketch.profiles.item(0)
                    ExtrudeCollection.add(Profile)
                    extrude = rootComp.features.extrudeFeatures                    
                    Distance = adsk.core.ValueInput.createByReal(BoxSize)
                    ExtrudeBody = extrude.addSimple(Profile, Distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    createdPixel = ExtrudeBody.bodies.item(0)
                    createdPixel.isSelectable = False
                    MovedPixel = createdPixel.moveToComponent(QRComp)
                    CombineCollection.add(MovedPixel)
                    QRSketch.deleteMe()
                    Feature = QRComp.component.features.item(0)
                    Feature.dissolve()
                    progressDialog.progressValue = PixelCount
                    PixelCount += 1
        progressDialog.hide()
        Combine = QRComp.component.features.combineFeatures
        Combine.createInput(QRComp.bRepBodies.item(0), CombineCollection)
        CombineCollection.removeByIndex(0)
        input: adsk.fusion.CombineFeatureInput = Combine.createInput(QRComp.bRepBodies.item(0), CombineCollection)
        input.isNewComponent = False
        input.isKeepToolBodies = False
        input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combineFeature = Combine.add(input)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def SpherePixels(Text, Size):
    Plane: adsk.fusion.ConstructionPlane
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design: adsk.fusion.Design = app.activeProduct         
        rootComp: adsk.fusion.Component = design.rootComponent    
        QRComp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        QRComp.component.name = f"QR Code: {Text}"
        qr = qrcode.QRCode(box_size=1, border=0)
        qr.add_data(Text)
        qr.make(fit=True)
        qrMatrix = qr.get_matrix()
        FilletCollection = adsk.core.ObjectCollection.create()
        ExtrudeCollection = adsk.core.ObjectCollection.create()
        progressDialog = ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.isCancelButtonShown = True
        True_Count = sum(row.count(True) for row in qrMatrix)
        progressDialog.show('Progress Dialog', f"%p% Completed\n%v of %m", 0, True_Count)
        PixelCount = 1
        BoxSize = Size
        Start_x, Start_Y = 0,0
        QRSketch = rootComp.sketches.addWithoutEdges(rootComp.xYConstructionPlane)
        for row_idx, row in enumerate(qrMatrix):
            if progressDialog.wasCancelled:
                break
            for col_idx, cell in enumerate(row):
                if progressDialog.wasCancelled:
                    break
                if cell == True:
                    x = Start_x + col_idx * BoxSize
                    y = Start_Y + row_idx * BoxSize
                    rect_points = [
                        adsk.core.Point3D.create(x, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y + BoxSize, 0),
                        adsk.core.Point3D.create(x, y + BoxSize, 0)
                    ]
                    
                    #Square = QRSketch.sketchCurves.sketchLines.addTwoPointRectangle(rect_points[0], rect_points[2]) 
                    Line = adsk.core.Line3D.create(rect_points[0], rect_points[2])
                    (__, SP, EP) = Line.evaluator.getParameterExtents()
                    (__, MP) = Line.evaluator.getPointAtParameter((SP + EP) / 2)
                    RLine = adsk.core.Line3D.create(rect_points[0], rect_points[1])
                    LineLength = Line.startPoint.distanceTo(Line.endPoint)
                    Circle = QRSketch.sketchCurves.sketchCircles.addByCenterRadius(MP, LineLength / 3)
                    progressDialog.progressValue = PixelCount
                    PixelCount += 1
        for Profile in QRSketch.profiles:
            ExtrudeCollection.add(Profile)
        extrude = QRComp.component.features.extrudeFeatures                    
        Distance = adsk.core.ValueInput.createByReal(LineLength - LineLength / 3)
        ExtrudeBody = extrude.addSimple(ExtrudeCollection, Distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ExtrudeBody.dissolve()
        QRSketch.deleteMe()
        progressDialog.hide()
        FilletEdgeSet = []
        for Body in QRComp.bRepBodies:
            Body.isSelectable = False
            for edge in Body.edges:
                FilletCollection.add(edge)
        fillets = QRComp.component.features.filletFeatures
        radius1 = adsk.core.ValueInput.createByReal(Distance.realValue/2)
        FilletInput = fillets.createInput()
        FilletInput.isRollingBallCorner = True
        constRadiusInput = FilletInput.edgeSetInputs.addConstantRadiusEdgeSet(FilletCollection, radius1, True)
        constRadiusInput.continuity = adsk.fusion.SurfaceContinuityTypes.TangentSurfaceContinuityType
        
        fillet1 = fillets.add(FilletInput)
        fillet1.dissolve()
        #
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def CirclePixels(Text, Size):
    Plane: adsk.fusion.ConstructionPlane
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design: adsk.fusion.Design = app.activeProduct         
        rootComp: adsk.fusion.Component = design.rootComponent    
        QRComp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        QRComp.component.name = f"QR Code: {Text}"
        qr = qrcode.QRCode(box_size=1, border=0)
        qr.add_data(Text)
        qr.make(fit=True)
        qrMatrix = qr.get_matrix()
        FilletCollection = adsk.core.ObjectCollection.create()
        ExtrudeCollection = adsk.core.ObjectCollection.create()
        progressDialog = ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.isCancelButtonShown = True
        True_Count = sum(row.count(True) for row in qrMatrix)
        progressDialog.show('Progress Dialog', f"%p% Completed\n%v of %m", 0, True_Count)
        PixelCount = 1
        BoxSize = Size
        Start_x, Start_Y = 0,0
        QRSketch = rootComp.sketches.addWithoutEdges(rootComp.xYConstructionPlane)
        for row_idx, row in enumerate(qrMatrix):
            if progressDialog.wasCancelled:
                break
            for col_idx, cell in enumerate(row):
                if progressDialog.wasCancelled:
                    break
                if cell == True:
                    x = Start_x + col_idx * BoxSize
                    y = Start_Y + row_idx * BoxSize
                    rect_points = [
                        adsk.core.Point3D.create(x, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y, 0),
                        adsk.core.Point3D.create(x + BoxSize, y + BoxSize, 0),
                        adsk.core.Point3D.create(x, y + BoxSize, 0)
                    ]
                    
                    #Square = QRSketch.sketchCurves.sketchLines.addTwoPointRectangle(rect_points[0], rect_points[2]) 
                    Line = adsk.core.Line3D.create(rect_points[0], rect_points[2])
                    (__, SP, EP) = Line.evaluator.getParameterExtents()
                    (__, MP) = Line.evaluator.getPointAtParameter((SP + EP) / 2)
                    RLine = adsk.core.Line3D.create(rect_points[0], rect_points[1])
                    LineLength = Line.startPoint.distanceTo(Line.endPoint)
                    Circle = QRSketch.sketchCurves.sketchCircles.addByCenterRadius(MP, LineLength / 3)
                    progressDialog.progressValue = PixelCount
                    PixelCount += 1
        for Profile in QRSketch.profiles:
            ExtrudeCollection.add(Profile)
        extrude = QRComp.component.features.extrudeFeatures                    
        Distance = adsk.core.ValueInput.createByReal(1)
        ExtrudeBody = extrude.addSimple(ExtrudeCollection, Distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ExtrudeBody.dissolve()
        QRSketch.deleteMe()
        for body in QRComp.bRepBodies:
            body.isSelectable = False
        progressDialog.hide()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))