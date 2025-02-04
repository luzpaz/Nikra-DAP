# ************************************************************************************
# *                                                                                  *
# *   Copyright (c) 2022 Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>            *
# *   Copyright (c) 2022 Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>   *
# *   Copyright (c) 2022 Dewald Hattingh (UP) <u17082006@tuks.co.za>                 *
# *   Copyright (c) 2022 Varnu Govender (UP) <govender.v@tuks.co.za>                 *
# *                                                                                  *
# *   This program is free software; you can redistribute it and/or modify           *
# *   it under the terms of the GNU Lesser General Public License (LGPL)             *
# *   as published by the Free Software Foundation; either version 2 of              *
# *   the License, or (at your option) any later version.                            *               
# *   for detail see the LICENCE text file.                                          *
# *                                                                                  *
# *   This program is distributed in the hope that it will be useful,                *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of                 *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  *
# *   GNU Library General Public License for more details.                           *
# *                                                                                  *
# *   You should have received a copy of the GNU Library General Public              *   
# *   License along with this program; if not, write to the Free Software            *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307           *
# *   USA                                                                            *
# *_________________________________________________________________________________ *        
# *                                                                                  *
# *     Nikra-DAP FreeCAD WorkBench (c) 2022:                                        *
# *        - Please refer to the Documentation and README                            *
# *          for more information regarding this WorkBench and its usage.            *
# *                                                                                  *
# *     Author(s) of this file:                                                      *                         
# *        -  Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>                       * 
# *        -  Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>              *
# ************************************************************************************


import FreeCAD
import os
import DapTools
from DapTools import addObjectProperty
from pivy import coin
from FreeCAD import Units
import Part
from math import sin, cos, pi

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore


JOINT_TYPES = ["Rotation", "Linear Movement"]

DEFINITION_MODES = [["1 Point + 2 Bodies",
                     "alt def mode"], ["2 Points + 2 Bodies"]]

HELPER_TEXT = [["Choose a point (by picking an LCS) and the two bodies attached to the point.",\
    "Alternative Deifinition Mode Description"],\
    ["Choose two points (by picking two LCS's) and two bodies, (each point must be attached to its own body)"]]

YES_NO = ["No", "Yes"]

FUNCTION_TYPES = ["Not Applicable", "Function type 'a'", "Function type 'b'", "Function type 'c'"]

def makeDapJoints(name="DapRelativeMovement"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _DapJoint(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapJoint(obj.ViewObject)
    return obj


class _CommandDapJoint:
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon4.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Joint", "Add New Relative Movement Between 2 Bodies"),
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Joint", "Add a new relative movement between two bodies to the DAP analysis.")}

    def IsActive(self):
        return DapTools.getActiveAnalysis() is not None

    def Activated(self):
        #FreeCAD.ActiveDocument.openTransaction("Create CfdFluidBoundary")
        #FreeCADGui.doCommand("")
        #FreeCADGui.addModule("CfdFluidBoundary")
        #FreeCADGui.addModule("DapTools")
        #FreeCADGui.doCommand("DapTools.getActiveAnalysis().addObject(CfdFluidBoundary.makeCfdFluidBoundary())")
        #FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)
        import DapTools
        import DapJointSelection
        DapTools.getActiveAnalysis().addObject(DapJointSelection.makeDapJoints())
        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Joint', _CommandDapJoint())


class _DapJoint:
    def __init__(self, obj):

        obj.Proxy = self
        self.Type = "DapJoint"

        self.initProperties(obj)

    def initProperties(self, obj):
        #addObjectProperty(obj, 'References', [], "App::PropertyStringList", "", "List of Parts")
        all_subtypes = []
        for s in DEFINITION_MODES:
            all_subtypes += s
        addObjectProperty(obj, 'RelMovDefinitionMode', all_subtypes, "App::PropertyEnumeration","", \
            "Define the relative movement between 2 bodies")
        addObjectProperty(obj, 'TypeOfRelMov', JOINT_TYPES, "App::PropertyEnumeration", "", "Type of Relative Movement")
        addObjectProperty(obj, 'CoordPoint1RelMov', FreeCAD.Vector(0,0,0), "App::PropertyVector", "",\
            "Point 1 used to define relative movement between 2 bodies")
        addObjectProperty(obj, 'CoordPoint2RelMov', FreeCAD.Vector(0,0,0), "App::PropertyVector", "",\
            "Point 2 used to define relative movement between 2 bodies")
        addObjectProperty(obj, 'Body1', "Ground", "App::PropertyString", "", "Label: Body 1")
        addObjectProperty(obj, 'Body2', "Ground", "App::PropertyString", "", "Label: Body 2")
        addObjectProperty(obj, 'Point1RelMov', "", "App::PropertyString", "", "Label: Point 1 of Relative Movement")
        addObjectProperty(obj, 'Point2RelMov', "", "App::PropertyString", "", "Label: Point 2 of Relative Movement")
        addObjectProperty(obj, 'DriverOn', YES_NO, "App::PropertyEnumeration","",\
            "Is a 'driver' switched on to control the defined relative movement?")
        addObjectProperty(obj, 'DriverFunctionType', FUNCTION_TYPES, "App::PropertyEnumeration", "",\
            "Function type that the (switched on) 'driver' will use to control the defined relative movement." )
        addObjectProperty(obj, 'tEndDriverFuncTypeA', "", "App::PropertyQuantity", "",\
            "Driver Function Type A: End time (t_end)")
        addObjectProperty(obj, 'coefC1DriverFuncTypeA', "", "App::PropertyQuantity", "",\
            "Driver Function Type A: coefficient 'c_1'")
        addObjectProperty(obj, 'coefC2DriverFuncTypeA', "", "App::PropertyQuantity", "",\
            "Driver Function Type A: coefficient 'c_2'")
        addObjectProperty(obj, 'coefC3DriverFuncTypeA', "", "App::PropertyQuantity", "",\
            "Driver Function Type A: coefficient 'c_3'")
        addObjectProperty(obj, 'tStartDriverFuncTypeB', "", "App::PropertyQuantity", "",\
            "Driver Function Type B: Start time (t_start)")
        addObjectProperty(obj, 'tEndDriverFuncTypeB', "", "App::PropertyQuantity", "",\
            "Driver Function Type B: End time (t_end)")
        addObjectProperty(obj, 'initialValueDriverFuncTypeB', "", "App::PropertyQuantity", "",\
            "Driver Function Type B: initial function value")
        addObjectProperty(obj, 'endValueDriverFuncTypeB', "", "App::PropertyQuantity", "",\
            "Driver Function Type B: function value at t_end")
        addObjectProperty(obj, 'tStartDriverFuncTypeC', "", "App::PropertyQuantity", "",\
            "Driver Function Type C: Start time (t_start)")
        addObjectProperty(obj, 'tEndDriverFuncTypeC', "", "App::PropertyQuantity", "",\
            "Driver Function Type C: End time (t_end)")
        addObjectProperty(obj, 'initialValueDriverFuncTypeC', "", "App::PropertyQuantity", "",\
            "Driver Function Type C: initial function value")
        addObjectProperty(obj, 'endDerivativeDriverFuncTypeC', "", "App::PropertyQuantity", "",\
            "Driver Function Type C: function derivative at t_end")
        
        
        #NOTE: hiding all properties that have anything to do with functions until the python code works
        obj.setEditorMode("DriverOn", 2)
        obj.setEditorMode("DriverFunctionType", 2)
        obj.setEditorMode("tEndDriverFuncTypeA", 2)
        obj.setEditorMode("coefC1DriverFuncTypeA", 2)
        obj.setEditorMode("coefC2DriverFuncTypeA", 2)
        obj.setEditorMode("coefC3DriverFuncTypeA", 2)
        obj.setEditorMode("tStartDriverFuncTypeB", 2)
        obj.setEditorMode("tEndDriverFuncTypeB", 2)
        obj.setEditorMode("initialValueDriverFuncTypeB", 2)
        obj.setEditorMode("endValueDriverFuncTypeB", 2)
        obj.setEditorMode("tStartDriverFuncTypeC", 2)
        obj.setEditorMode("tEndDriverFuncTypeC", 2)
        obj.setEditorMode("initialValueDriverFuncTypeC", 2)
        obj.setEditorMode("endDerivativeDriverFuncTypeC", 2)
        #obj.setEditorMode("DriverOn", 2)
        
        
        
        obj.tEndDriverFuncTypeA = Units.Unit("")
        obj.coefC1DriverFuncTypeA = Units.Unit("")
        obj.coefC2DriverFuncTypeA = Units.Unit("")
        obj.coefC3DriverFuncTypeA = Units.Unit("")
        
        obj.tStartDriverFuncTypeB = Units.Unit("")
        obj.tEndDriverFuncTypeB = Units.Unit("")
        obj.initialValueDriverFuncTypeB = Units.Unit("")
        obj.endValueDriverFuncTypeB = Units.Unit("")

        obj.tStartDriverFuncTypeC = Units.Unit("")
        obj.tEndDriverFuncTypeC = Units.Unit("")
        obj.initialValueDriverFuncTypeC = Units.Unit("")
        obj.endDerivativeDriverFuncTypeC = Units.Unit("")

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create joint representation part at recompute. """
        #TODO visual representation of the joint should only be vissible if the joint definition mode was correctly specified, e.g. rotation joint needs 1 point AND 2 seperate bodies, translation joint needs 2 points AND 2 bodies
            
        doc_name = str(obj.Document.Name)
        doc = FreeCAD.getDocument(doc_name)
        
        # if LCS positions were changed then the new co-ordinates should be calculated.
        # this is a wastefull way of achieving this, since the objects coordinates are changed
        # within the ui
        if obj.Point1RelMov != "":
            lcs_obj = doc.getObjectsByLabel(obj.Point1RelMov)[0]
            obj.CoordPoint1RelMov = lcs_obj.Placement.Base
        if obj.Point2RelMov != "":
            lcs_obj = doc.getObjectsByLabel(obj.Point2RelMov)[0]
            obj.CoordPoint2RelMov = lcs_obj.Placement.Base
        
        
        scale_param = 50000

        joint_index = DapTools.indexOrDefault(JOINT_TYPES, obj.TypeOfRelMov, 0)
        
        

        if joint_index == 0 and obj.Point1RelMov != "":

            vol_counter = 0
            vol = 0
            if obj.Body1 != "Ground":
                body1 = doc.getObjectsByLabel(obj.Body1)
                vol += body1[0].Shape.Volume
                vol_counter += 1
            if obj.Body2 != "Ground":
                body2 = doc.getObjectsByLabel(obj.Body2)
                vol += body2[0].Shape.Volume
                vol_counter += 1
            if vol_counter >0:
                vol = vol/vol_counter
            else:
                vol = 100000
            
            

            scale_factor = vol/scale_param
            r1 = 7*scale_factor
            r2 = scale_factor
            torus_dir = FreeCAD.Vector(0, 0, 1)
            torus = Part.makeTorus(r1, r2, obj.CoordPoint1RelMov, torus_dir, -180, 180, 240)
            cone1_pos = obj.CoordPoint1RelMov + FreeCAD.Vector(r1, -5*r2, 0)
            cone1_dir = FreeCAD.Vector(0, 1, 0)
            cone1 = Part.makeCone(0, 2*r2, 5*r2, cone1_pos, cone1_dir)
            cone2_pos_x = obj.CoordPoint1RelMov.x -r1*cos(pi/3) + 5*r2*cos(pi/6)
            cone2_pos_y = obj.CoordPoint1RelMov.y -r1*sin(pi/3) - 5*r2*sin(pi/6)
            cone2_pos = FreeCAD.Vector(cone2_pos_x, cone2_pos_y, 0)
            cone2_dir = FreeCAD.Vector(-cos(pi/6), sin(pi/6), 0)
            cone2 = Part.makeCone(0, 2*r2, 5*r2, cone2_pos, cone2_dir)
            torus_w_arrows = Part.makeCompound([torus, cone1, cone2])
            obj.Shape = torus_w_arrows
            obj.ViewObject.ShapeColor = (1.0, 0.843137264251709, 0.0, 0.6000000238418579)

        elif joint_index == 1 and obj.Point1RelMov != "" and obj.Point2RelMov != "":
            l = (obj.CoordPoint2RelMov - obj.CoordPoint1RelMov).Length
            if l > 1e-6 and obj.Point1RelMov != "":
                lin_move_dir = (obj.CoordPoint2RelMov - obj.CoordPoint1RelMov).normalize()
                cylinder = Part.makeCylinder(0.05*l, 0.5*l, obj.CoordPoint1RelMov + 0.25*l*lin_move_dir, lin_move_dir)
                cone1 = Part.makeCone(0, 0.1*l, 0.25*l, obj.CoordPoint1RelMov, lin_move_dir)
                cone2 = Part.makeCone(0, 0.1*l, 0.25*l, obj.CoordPoint2RelMov, -lin_move_dir)
                double_arrow = Part.makeCompound([cylinder, cone1, cone2])
                obj.Shape = double_arrow
                obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0, 0.0)
            else:
                #adding a checker to make sure the error does not come up when first instantiating a new undefined joint
                obj.Shape = Part.Shape()
                if obj.Point1RelMov != "" and obj.Point2RelMov != "":
                    FreeCAD.Console.PrintError(f"The selected 2 points either coincide, or are too close together!!!")
        else:
            obj.Shape = Part.Shape()

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
    
class _ViewProviderDapJoint:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon4.png")
        return icon_path

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.standard = coin.SoGroup()
        vobj.addDisplayMode(self.standard, "Standard")
        #self.ViewObject.Transparency = 95
        return

    def getDisplayModes(self, obj):
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        return "Shaded"

    def setDisplayMode(self,mode):
        return mode

    def updateData(self, obj, prop):
        return

    def onChanged(self, vobj, prop):
        #DapTools.setCompSolid(vobj)
        return

    def doubleClicked(self, vobj):
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            FreeCAD.Console.PrintError('Task dialog already active\n')
        return True

    def setEdit(self, vobj, mode):
        import _TaskPanelDapJoint
        taskd = _TaskPanelDapJoint.TaskPanelDapJoint(self.Object)
        FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
