import bpy
from bpy.types import Operator

from . fsc_bool_util import *

class FSC_OT_Remesh_Operator(Operator):
    bl_idname = "object.fsc_remesh"
    bl_label = "Remesh"
    bl_description = "Voxel remesh operator" 
    bl_options = {'REGISTER', 'UNDO'} 

    def invoke(self, context, event):
        execute_remesh(context) 
        return {'FINISHED'}