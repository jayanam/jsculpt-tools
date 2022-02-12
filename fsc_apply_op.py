import bpy
from bpy.types import Operator
from . utils.fsc_select_mode_utils import *

class FSC_OT_ApplyAllModifiersOperator(Operator):
    bl_idname = "object.fsc_apply_all_mod_op"
    bl_label = ""
    bl_description = "Apply all modifiers for selected objects" 
    bl_options = {'REGISTER', 'UNDO'} 

    @classmethod
    def poll(cls, context):
      return len(context.selected_objects) > 0

    def apply_all_modifiers(self, context):
      for obj in context.selected_objects[:]:
          for modifier in obj.modifiers[:]:
              bpy.context.view_layer.objects.active = obj
              bpy.ops.object.modifier_apply(modifier=modifier.name)

    def execute(self, context):
      mode = get_mode()
      to_object()
      self.apply_all_modifiers(context)
      to_mode(mode)
      return {'FINISHED'}