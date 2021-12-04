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

    def __init__(self):
        self.draw_handle_2d = None

    @classmethod
    def poll(cls, context): 

        if context.object is None:
            return False

        if context.object.mode != "SCULPT":
          return False

        if context.window_manager.in_modal_mode:
            return False

        return True


    def invoke(self, context, event):
        args = (self, context)
        context.window_manager.in_modal_mode = True
        self.register_handlers(args, context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def register_handlers(self, args, context):
        self.draw_handle_2d = bpy.types.SpaceView3D.draw_handler_add(
        self.draw_callback_2d, args, "WINDOW", "POST_PIXEL")
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)

    def unregister_handlers(self, context):
        context.window_manager.in_modal_mode = False
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_2d, "WINDOW")
        
        self.draw_handle_2d = None
        self.draw_event  = None

    def finish(self):
      bpy.context.window_manager.in_modal_mode = False
      self.unregister_handlers(bpy.context)
      return {"FINISHED"}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        if event.type == "ESC" and event.value == "PRESS":
            return self.finish()

        if self.handle_select(context, event):
          if event.ctrl:
            return self.finish()

          return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def get_active_str(self):
      obj = get_active()
      if obj:
        return obj.name
      else:
        return "None"

    def draw_callback_2d(self, op, context):

        # Draw text for add object mode
        header = "- Select Object Mode [ {0} ] -"
        text = "Left Click = Select | Esc = Exit"

        blf.color(0, 0.0, 0.5, 1, 1)
        blf.color(1, 1, 1, 1, 1)
        blf.size(0, 20, 72)
        blf.size(1, 16, 72)

        region = context.region
        xt = int(region.width / 2.0)

        header  = header.format(self.get_active_str())

        blf.position(0, xt - blf.dimensions(0, header)[0] / 2, 50 , 0)
        blf.draw(0, header)

        blf.position(1, xt - blf.dimensions(1, text)[0] / 2, 20 , 0)
        blf.draw(1, text)

    def handle_select(self, context, event)                           :
        if event.value == "PRESS" and event.type == "LEFTMOUSE":
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