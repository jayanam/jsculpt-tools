import bpy
from bpy.types import Operator

from bpy.props import BoolProperty

from . utils.fsc_bool_util import *
from . utils.fsc_retopo_utils import *

class FSC_OT_Remesh_Operator(Operator):
    bl_idname = "object.fsc_remesh"
    bl_label = "Remesh"
    bl_description = "Voxel remesh operator" 
    bl_options = {'REGISTER', 'UNDO'}

    join_b4_remesh : BoolProperty(name="Join", options={'HIDDEN'}, default=False)

    def invoke(self, context, event):

        # Apply all mirror modifiers before join and remesh
        for sel_object in context.selected_objects:
            for modifier in sel_object.modifiers:
                if modifier.type == "MIRROR":
                    bpy.ops.object.modifier_apply(modifier=modifier.name)

        if self.join_b4_remesh:
            bpy.ops.object.join()

        execute_remesh(context) 
        return {'FINISHED'}