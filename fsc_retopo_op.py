import bpy
from bpy.types import Operator
from bpy_extras import object_utils

from . utils.fsc_retopo_utils import add_mirror, add_shrinkwrap, set_retopo_settings

from . utils.fsc_bool_util import *
from . utils.fsc_select_mode_utils import *

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

      set_retopo_settings(context)

      is_cursor_loc = context.scene.retopo_location == "Cursor"
      loc_plane = (0,0,0)
      if is_cursor_loc:
          loc_plane = bpy.context.scene.cursor.location

      if context.scene.retopo_mesh == "Plane":
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=loc_plane)
      else:
        mesh = bpy.data.meshes.new("")
        mesh.vertices.add(1)
        object_utils.object_data_add(context, mesh, operator=None)
      
      retopo_object = bpy.context.view_layer.objects.active
      retopo_object.name = "retopo mesh"
      
      add_shrinkwrap(retopo_object, context)

      if context.scene.add_retopo_mirror != "None":

        # Reset location to zero for mirror and location type cursor
        if is_cursor_loc:
          bpy.context.scene.cursor.location = (0, 0, 0)
          bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
          bpy.context.scene.cursor.location = loc_plane

        add_mirror(retopo_object, context)

      to_edit()

      bpy.ops.mesh.normals_make_consistent()

      return {'FINISHED'}