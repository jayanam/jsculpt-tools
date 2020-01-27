import bpy
import blf

from bpy.types import Operator

from mathutils import Vector

from bpy_extras import view3d_utils

from . fsc_select_mode_utils import *

class FSC_OT_Add_Oject_Operator(Operator):
    bl_idname = "object.fsc_add_object"
    bl_label = "Add object"
    bl_description = "Add object in sculpt mode" 
    bl_options = {'REGISTER', 'UNDO'} 

    def __init__(self):
        self.draw_handle_2d = None

    def invoke(self, context, event):
        args = (self, context)
        context.window_manager.in_add_mode = True
        self.register_handlers(args, context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def register_handlers(self, args, context):
        self.draw_handle_2d = bpy.types.SpaceView3D.draw_handler_add(
        self.draw_callback_2d, args, "WINDOW", "POST_PIXEL")
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)

    def unregister_handlers(self, context):
        context.window_manager.in_add_mode = False
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_2d, "WINDOW")
        
        self.draw_handle_2d = None
        self.draw_event  = None

    def draw_callback_2d(self, op, context):

        # Draw text for add object mode
        header = "- Add Object Mode (Type: " + context.scene.add_object_type + ") -"
        text = "Ctrl + Left Click = Add | Esc = Exit"

        blf.color(1, 1, 1, 1, 1)
        blf.size(0, 20, 72)
        blf.size(1, 16, 72)

        region = context.region
        xt = int(region.width / 2.0)

        blf.position(0, xt - blf.dimensions(0, header)[0] / 2, 50 , 0)
        blf.draw(0, header)

        blf.position(1, xt - blf.dimensions(1, text)[0] / 2, 20 , 0)
        blf.draw(1, text)


    @classmethod
    def poll(cls, context): 

        if context.object is None:
            return False

        if context.window_manager.in_add_mode:
            return False

        return True

    def finish(self):
        context.window_manager.in_add_mode = False
        self.unregister_handlers(bpy.context)
        return {"FINISHED"}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        if event.type == "ESC" and event.value == "PRESS":
            context.window_manager.in_add_mode = False
            self.unregister_handlers(context)
            return {'FINISHED'}

        if event.value == "PRESS" and event.type == "LEFTMOUSE" and event.ctrl:
            mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            self.add_object(context, mouse_pos)

        return {'PASS_THROUGH'}

    def get_axis_no(self, str_axis):
        if str_axis == "X":
            return 0
        elif str_axis == "Y":
            return 1
        
        return 2


    def add_object(self, context, mouse_pos):
        
        scene = context.scene
        to_object()
        
        region = context.region
        region3D = context.space_data.region_3d

        view_vector = view3d_utils.region_2d_to_vector_3d(region,   region3D, mouse_pos)
        origin      = view3d_utils.region_2d_to_origin_3d(region,   region3D, mouse_pos)
        loc         = view3d_utils.region_2d_to_location_3d(region, region3D, mouse_pos, view_vector)
        rot         = (0,0,0)  

        # Get intersection and create objects at this location if possible
        hit, loc_hit, norm, face, *_ = scene.ray_cast(context.view_layer, origin, view_vector)
        if hit:
            loc = loc_hit
            z = Vector((0,0,1))
            
            if context.scene.align_to_face:
                rot = z.rotation_difference( norm ).to_euler()

        obj_type = context.scene.add_object_type
      
        # TODO: Add more init options here
        if obj_type == "Sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, location=loc)
        if obj_type == "Plane":
            bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=loc, rotation=rot)
        elif obj_type == "Cube":  
            bpy.ops.mesh.primitive_cube_add(enter_editmode=False, location=loc, rotation=rot)
        elif obj_type == "Cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, enter_editmode=False, location=loc, rotation=rot)
        elif obj_type == "Torus":
            bpy.ops.mesh.primitive_torus_add(align='WORLD', location=loc, rotation=rot, major_radius=1, minor_radius=0.25, abso_major_rad=1.25, abso_minor_rad=0.75)
        elif obj_type == "Cone":
            bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, enter_editmode=False, location=loc, rotation=rot)
        elif obj_type == "Icosphere":
            bpy.ops.mesh.primitive_ico_sphere_add(radius=1, enter_editmode=False, location=loc, rotation=rot)
 
        elif obj_type == "Scene":
            custom_obj = context.scene.add_scene_object
            if custom_obj:

                deselect_all()
                make_active(custom_obj)

                bpy.ops.object.duplicate(linked=True)
                clone_custom = bpy.context.view_layer.objects.active
                bpy.ops.object.make_single_user(object=True, obdata=True)

                clone_custom.location = loc
                clone_custom.rotation_euler = rot

                deselect_all()
                make_active(clone_custom)

                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


        # Check if we need to add mirror modifier
        mirror = context.scene.add_object_mirror

        if mirror != "None":

            active_obj = bpy.context.active_object
            old_loc = active_obj.location.copy()

            bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
            mirror_mod = active_obj.modifiers.new(type="MIRROR", name="FSC_MIRROR")
            mirror_mod.use_axis[0] = False
            mirror_mod.use_axis[self.get_axis_no(mirror)] = True

            # Set the pivot point back to the old position of the object
            bpy.context.scene.cursor.location = old_loc

        to_sculpt()