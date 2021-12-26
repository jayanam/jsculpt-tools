import bpy
from bpy.types import Operator
from bpy_extras import object_utils

from . utils.fsc_retopo_utils import add_subsurf

from . utils.fsc_select_mode_utils import *

class FSC_OT_Subsurf_Operator(Operator):
    bl_idname = "object.fsc_subsurf"
    bl_label = "Add Subsurf Modifier"
    bl_description = "Add Subsurf Modifier if not exists" 
    bl_options = {'REGISTER', 'UNDO'} 

    @classmethod
    def poll(cls, context):
        return context.view_layer.objects.active is not None

    def invoke(self, context, event):

      mod_subsurf = add_subsurf(context.view_layer.objects.active, context)

      return {'FINISHED'}