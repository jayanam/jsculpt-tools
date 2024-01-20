import blf
import bmesh
import bpy

from bpy.props import *

from . utils.fsc_bool_util import *

from . types.vertices import *
from . utils.fsc_view_utils import *
from . utils.fsc_select_mode_utils import *
from . utils.fsc_retopo_utils import add_mirror, set_retopo_settings
from . utils.textutils import *

from . fsc_draw_base_op import *

# Draw mode operator
class FSC_OT_Draw_Mode_Operator(FSC_OT_Draw_Base_Operator):
    bl_idname = "object.fsc_draw_retopo"
    bl_label = "Draw Mode Operator"
    bl_description = "Draw Mode Operator"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        result = "PASS_THROUGH"
                              
        if event.type == "ESC" and event.value == "PRESS":
            return self.finish()

        if event.type == "RET" and event.value == "PRESS":
            self.to_mesh(context, event.ctrl)
            return self.finish()

        # The mouse is moved
        if event.type == "MOUSEMOVE":
            pass
            
        # Left mouse button is released
        if event.value == "RELEASE" and event.type == "LEFTMOUSE":
            pass

        # Left mouse button is pressed
        if event.value == "PRESS" and event.type == "LEFTMOUSE":
            if event.ctrl:
                mouse_pos_2d = (event.mouse_region_x, event.mouse_region_y)
                mouse_pos_3d, hit_object = get_3d_for_2d(mouse_pos_2d, context)
                if mouse_pos_3d and hit_object:
                    self.points.append(mouse_pos_3d)
                    context.scene.retopo_object = hit_object
                    make_active(hit_object)
                    result = "RUNNING_MODAL"

        return { result }

    def to_mesh(self, context, close_mesh):
        vertices = self.points.get_vertices().copy()
        if vertices:

            # Create a mesh using BMesh
            mesh = bpy.data.meshes.new("Retopo mesh data")
            retopo_mesh  = bpy.data.objects.new("retopo mesh", mesh)
            bpy.context.scene.collection.objects.link(retopo_mesh)

            bm = bmesh.new()
            bm.from_mesh(mesh) 

            for v in vertices:
                bm.verts.new(v)

            if close_mesh:
                bmesh.ops.contextual_create(bm, geom=list(bm.verts))
            else:
                bm.verts.ensure_lookup_table()
                for i in range(len(bm.verts)-1):
                    bm.edges.new((bm.verts[i], bm.verts[i+1]))

            bm.to_mesh(mesh)
            bm.free()

            to_object()

            select_active(retopo_mesh)

            context.scene.retopo_mesh = retopo_mesh

            set_retopo_settings(context)

            if context.scene.add_retopo_mirror != "None":
                context.scene.cursor.location = (0, 0, 0)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                context.scene.cursor.location = context.scene.cursor.location
                add_mirror(retopo_mesh, context)

            # Switch to edit mode and select mesh
            to_edit()
            select_mesh()


	# Draw handler to paint in pixels
    def draw_callback_2d(self, op, context):

        region = context.region
        xt = int(region.width / 2.0)

        # Draw text for draw mode
        blf_set_size(0, 22)
        blf.color(0, 1, 1, 1, 1)

        blf_set_size(1, 16)
        blf.color(1, 1, 1, 1, 1)

        title = "- Draw Retopo Mesh -"
        desc = "Ctrl + Click: Add points, Enter: Create, Ctrl + Enter: Create closed"

        blf.position(0, xt - blf.dimensions(0, title)[0] / 2, 45, 0)
        blf.draw(0, title)

        blf.position(1, xt - blf.dimensions(1, desc)[0] / 2, 20, 0)
        blf.draw(1, desc)