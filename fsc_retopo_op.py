import bpy
from bpy.types import Operator
from . fsc_common_utils import get_axis_no

from . fsc_bool_util import *
from . fsc_select_mode_utils import *

class FSC_OT_Retopo_Operator(Operator):
    bl_idname = "object.fsc_retopo"
    bl_label = "Create Retopo Mesh"
    bl_description = "Create a retopo mesh" 
    bl_options = {'REGISTER', 'UNDO'} 

    @classmethod
    def poll(cls, context):
        return context.scene.retopo_object is not None

    def invoke(self, context, event):

      make_active(context.scene.retopo_object)

      to_object()

      deselect_all()

      make_active(context.scene.retopo_object)

      my_areas = context.workspace.screens[0].areas

      for area in my_areas:
          for space in area.spaces:
              if space.type == 'VIEW_3D':
                  space.shading.show_backface_culling = True

      context.scene.tool_settings.snap_elements = {'FACE'}
      context.scene.tool_settings.use_snap_project = True
      context.scene.tool_settings.use_snap = True

      # TODO: Add it to location of retopo object?
      bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(0, 0, 0))

      plane = bpy.context.view_layer.objects.active
      mod_sw = plane.modifiers.new(type="SHRINKWRAP", name="FSC_SHRINKWRAP")
      mod_sw.target = context.scene.retopo_object
      mod_sw.wrap_mode = 'ABOVE_SURFACE'
      mod_sw.offset = 0.03

      if context.scene.add_retopo_subsurf:
        mod_subsurf = plane.modifiers.new(type="SUBSURF", name="FSC_SUBSURF")

      if context.scene.add_retopo_mirror:
        mod_mirror = plane.modifiers.new(type="MIRROR", name="FSC_MIRROR")
        mod_mirror.use_axis[0] = False
        mod_mirror.use_axis[get_axis_no(context.scene.add_retopo_mirror)] = True
        
      to_edit()

      bpy.ops.mesh.normals_make_consistent(inside=False)

      return {'FINISHED'}