import bpy
import blf
from bpy.types import Operator

from . fsc_select_mode_utils import *

from bpy_extras.view3d_utils import (
    region_2d_to_origin_3d,
    region_2d_to_location_3d, 
    region_2d_to_vector_3d,
    location_3d_to_region_2d
)

class FSC_OT_Select_Operator(Operator):
    bl_idname = "object.fsc_select_object"
    bl_label = "Select object in sculpt mode"
    bl_description = "Select object in sculpt mode" 
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context): 

        if context.object.mode != "SCULPT":
          return False

        return True

    def invoke(self, context, event):
        args = (self, context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self):
      return {"FINISHED"}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        self.handle_select(context, event)

        return self.finish()

    def handle_select(self, context, event)                           :
        pos_2d = (event.mouse_region_x, event.mouse_region_y)
        raycast_param = self.get_raycast_param(context.view_layer)
        origin, direction = self.get_origin_and_direction(pos_2d, context)
        hit, hit_loc, norm, face, hit_obj, *_ = context.scene.ray_cast(raycast_param, origin, direction)

        if hit:
            to_object()
            deselect_all()
            make_active(hit_obj)
            to_sculpt()              
            return True

        return False
          
    def get_origin_and_direction(self, pos_2d, context):
        region    = context.region
        region_3d = context.space_data.region_3d
        
        origin    = region_2d_to_origin_3d(region, region_3d, pos_2d)
        direction = region_2d_to_vector_3d(region, region_3d, pos_2d)

        return origin, direction

    def get_raycast_param(self, view_layer):        
        if bpy.app.version >= (2, 91, 0):
            return view_layer.depsgraph
        else:
            return view_layer