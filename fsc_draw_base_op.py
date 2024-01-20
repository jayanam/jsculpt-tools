import bpy
import blf

from bpy.types import Operator
from bpy.props import *

from . types.vertices import *

from . utils.textutils import *

# Draw base operator
class FSC_OT_Draw_Base_Operator(Operator):

    @classmethod
    def poll(cls, context): 

        # Check if we are already in draw mode
        if context.window_manager.in_draw_mode:
            return False

        return True

    def __init__(self):
        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.points = VertexContainer()


    def invoke(self, context, event):
        args = (self, context)  

        context.window_manager.in_draw_mode = True   

        # Register drawing handlers for 2d and 3d
        self.register_handlers(args, context)
                   
        # Register as modal operator
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def register_handlers(self, args, context):
        self.draw_handle_3d = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_3d, args, "WINDOW", "POST_VIEW")

        self.draw_handle_2d = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_2d, args, "WINDOW", "POST_PIXEL")
        
    def unregister_handlers(self, context):

        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_2d, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_3d, "WINDOW")
        
        self.draw_handle_2d = None
        self.draw_handle_3d = None

        context.window_manager.in_draw_mode = False

    def finish(self):
        self.unregister_handlers(bpy.context)
        return {"FINISHED"}

    # Draw handler to paint in pixels
    def draw_callback_2d(self, op, context):
        region = context.region
        xt = int(region.width / 2.0)

        # Draw text for draw mode
        blf_set_size(0,22)
        blf.color(0, 1, 1, 1, 1)

        blf_set_size(1, 16)
        blf.color(1, 1, 1, 1, 1)

        title = "- Ring Creation Mode -"

        if not self._line_shape.is_initialized():
            desc = "Ctrl + Click: Start to draw line"
        else:
            desc = "Click: Create ring"

        blf.position(0, xt - blf.dimensions(0, title)[0] / 2, 45, 0)
        blf.draw(0, title)

        blf.position(1, xt - blf.dimensions(1, desc)[0] / 2, 20, 0)
        blf.draw(1, desc)

	  # Draw handler to paint in 3d view
    def draw_callback_3d(self, op, context):        
        self.points.draw()