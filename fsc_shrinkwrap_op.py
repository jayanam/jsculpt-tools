import bpy
from bpy.types import Operator
from bpy_extras import object_utils

from . utils.fsc_retopo_utils import add_shrinkwrap

from . utils.fsc_select_mode_utils import *

class FSC_OT_Shrinkwrap_Operator(Operator):
    bl_idname = "object.fsc_shrinkwrap"
    bl_label = "Add Shrinkwrap Modifier"
    bl_description = "Add Shrinkwrap Modifier if not exists" 
    bl_options = {'REGISTER', 'UNDO'} 

    @classmethod
    def poll(cls, context):
        return context.view_layer.objects.active is not None

    def invoke(self, context, event):
        mod_shrinkwrap = add_shrinkwrap(context.view_layer.objects.active, context)
        return {'FINISHED'}