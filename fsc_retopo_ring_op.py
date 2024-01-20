import math
import blf
import bmesh
import bpy

from bpy.props import *

from . utils.fsc_bool_util import select_active

from . types.line_container import LineContainer

from . types.vertices import *
from . utils.fsc_view_utils import *
from . utils.fsc_select_mode_utils import *
from . utils.textutils import *

from . fsc_draw_base_op import *

# Draw mode operator
class FSC_OT_Retopo_Ring_Operator(FSC_OT_Draw_Base_Operator):
    bl_idname = "object.fsc_retopo_ring"
    bl_label = "Retopo Ring Operator"
    bl_description = "Retopo Ring Operator"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    def __init__(self):
        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.points = LineContainer()
        self.points_ring = VertexContainer()

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        result = "PASS_THROUGH"
                              
        if event.type == "ESC" and event.value == "PRESS":
            return self.finish()

        if event.type == "RET" and event.value == "PRESS":
            return self.finish()

        # The mouse is moved
        if event.type == "MOUSEMOVE":
            mouse_pos_2d = (event.mouse_region_x, event.mouse_region_y)
            mouse_pos_3d = get_3d_vertex(context, mouse_pos_2d)

            if mouse_pos_3d and self.points.is_initialized():
                self.points.set_vertex(1, mouse_pos_2d, mouse_pos_3d)
            
        # Left mouse button is released
        if event.value == "RELEASE" and event.type == "LEFTMOUSE":
            pass

        # Left mouse button is pressed
        if event.value == "PRESS" and event.type == "LEFTMOUSE":

            mouse_pos_2d = (event.mouse_region_x, event.mouse_region_y)

            mouse_pos_3d = get_3d_vertex(context, mouse_pos_2d)
            if mouse_pos_3d:

                if not self.points.is_initialized() and event.ctrl:
                    self.points.append(mouse_pos_2d, mouse_pos_3d)
                    self.points.append(mouse_pos_2d, mouse_pos_3d.copy())
                    result = "RUNNING_MODAL"

                elif self.points.is_initialized() :
                    self.project_loop_onto_object(context)

                    if self.has_retopo_mesh(context):
                        self.extend_retopo_mesh(context)
                    else:
                        self.create_retopo_mesh(context)

                    self.points.reset()
                    self.points_ring.reset()

                    result = "RUNNING_MODAL"

        return { result }

    def has_retopo_mesh(self, context):
        if context.scene.retopo_mesh:
            if len(context.scene.retopo_mesh.users_scene) == 0:
                context.scene.retopo_mesh = None    
            
        return context.scene.retopo_mesh != None

    def create_ring(self, retopo_obj, bm):
        new_verts = []
        new_edges = []
        for v in self.points_ring.get_vertices().copy():
            new_verts.append(bm.verts.new(v - retopo_obj.location))

        bm.verts.ensure_lookup_table()
        for i in range(len(new_verts)-1):
            new_edges.append(bm.edges.new((new_verts[i], new_verts[i+1])))
        new_edges.append(bm.edges.new((new_verts[-1], new_verts[0])))

        return new_verts, new_edges

    def extend_retopo_mesh(self, context):

        retopo_obj = context.scene.retopo_mesh
        retopo_mesh = retopo_obj.data

        bm = bmesh.from_edit_mesh(retopo_mesh) 

        selected_edges = [e for e in bm.edges if e.select]
        
        new_verts, new_edges = self.create_ring(retopo_obj, bm)

        bm.verts.sort()

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        deselect_mesh()

        for edge in new_edges:
            edge.select_set(True)

        connections = [v.index for v in new_verts]
        connections.append(connections[0])

        tknots, tpoints = self.get_space_points(bm, connections[:])

        splines = self.get_splines(bm, tknots, connections[:])

        move = []
        move.append(self.get_verts_to_move(tknots, tpoints, connections[:-1], splines))

        self.move_verts(retopo_obj, bm, move)

        bmesh.ops.bridge_loops(bm, edges=selected_edges + new_edges)

        bmesh.update_edit_mesh(retopo_mesh)

        to_object()
        
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')      

        to_edit()


    def create_retopo_mesh(self, context):
      
        retopo_mesh = bpy.data.meshes.new("Retopo_Ring_Mesh")
        retopo_obj  = bpy.data.objects.new("Retopo_Ring_Object", retopo_mesh)

        bpy.context.scene.collection.objects.link(retopo_obj)

        make_active(retopo_obj)

        to_object()

        context.scene.retopo_mesh = retopo_obj

        bpy.ops.object.select_all(action='DESELECT')

        bpy.context.view_layer.objects.active = retopo_obj
        retopo_obj.select_set(state=True)

        # Create a bmesh and add the vertices
        # added by mouse clicks
        bm = bmesh.new()
        bm.from_mesh(retopo_mesh) 

        new_verts, new_edges = self.create_ring(retopo_obj, bm)

        bm.to_mesh(retopo_mesh)

        connections = [v.index for v in new_verts]
        connections.append(connections[0])

        tconnections, tpoints = self.get_space_points(bm, connections[:])

        splines = self.get_splines(bm, tconnections, connections[:])

        move = []
        move.append(self.get_verts_to_move(tconnections, tpoints, connections[:-1], splines))

        self.move_verts(retopo_obj, bm, move)

        bm.to_mesh(retopo_mesh)
        bm.free()

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')        

        to_edit()

        bmesh.update_edit_mesh(retopo_obj.data, loop_triangles=True, destructive=True)

        if bpy.app.version >= (4, 0, 0):
            context.scene.tool_settings.use_snap_time_absolute = False
        else:
            context.scene.tool_settings.use_snap_project = False
            
        context.scene.tool_settings.use_snap = False

        select_mesh()


    # Move vertices to new location
    # Algorithm by Loop tools addon
    def move_verts(self, object, bm, move):

        for loop in move:
            for index, loc in loop:
                bm.verts[index].co = loc

        bm.normal_update()
        object.data.update()

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

    def get_verts_to_move(self, tconnections, tpoints, points, splines):
        move = []
        for p in points:
            m = tpoints[points.index(p)]
            if m in tconnections:
                n = tconnections.index(m)
            else:
                t = tconnections[:]
                t.append(m)
                t.sort()
                n = t.index(m) - 1
            if n > len(splines) - 1:
                n = len(splines) - 1
            elif n < 0:
                n = 0

            a, d, t, u = splines[n]
            move.append([p, ((m - t) / u) * d + a])

        return (move)

    def get_splines(self, bm_mod, tconnections, connections):
        splines = []
        for i in range(len(connections) - 1):
            a = bm_mod.verts[connections[i]].co
            b = bm_mod.verts[connections[i + 1]].co
            d = b - a
            t = tconnections[i]
            u = tconnections[i + 1] - t
            splines.append([a, d, t, u])

        return (splines)

    def get_space_points(self, bm_mod, connections):
        tconnections = []
        loc_prev = False
        len_total = 0
        for index in connections:
            loc = mathutils.Vector(bm_mod.verts[index].co[:])
            if not loc_prev:
                loc_prev = loc
            len_total += (loc - loc_prev).length
            tconnections.append(len_total)
            loc_prev = loc
        amount = len(connections)
        t_per_segment = len_total / (amount - 1)
        tpoints = [i * t_per_segment for i in range(amount)]

        return (tconnections, tpoints)


    def get_center_object(self, context):
        
        # 1. Get center of line (line_center)     
        # 2. raycast from line_center onto selected object (line_center_hit1)
        # 3. raycast from line_center_hit1 in the same direction (line_center_hit2)
        # 4. get center of line_center_hit1 and line_center_hit2 (center_object)

        origin, direction = get_origin_and_direction( self.points.get_center_2d(), context)

        _, line_center_hit1, _ = scene_raycast(direction, origin, context)

        _, line_center_hit2, _ = scene_raycast(direction, line_center_hit1 + (direction * 0.01), context)

        return get_center_vectors(line_center_hit1, line_center_hit2), direction

    def project_loop_onto_object(self, context):

        center_object, direction = self.get_center_object(context)

        # Draw cirle around center_object, diameter = line_length
        v1_n = (self.points.get_end_point() - self.points.get_start_point()).normalized()

        t = 0
        r = self.points.get_length() / 2

        circle_points = []

        while t < 2 * math.pi:
            circle_points.append(center_object + r * math.cos(t) * v1_n + r * math.sin(t) * direction)
            t += 2 * math.pi / 16

        hit_obj = None
        # raycast all points of the circle in direction to center_object and collect hit_points
        for cp in circle_points:
            hit, hit_vertex, hit_obj = scene_raycast(-(cp - center_object).normalized(), cp, context)
            if hit:
                self.points_ring.append(hit_vertex)

        if hit_obj:
          context.scene.retopo_object = hit_obj

	  # Draw handler to paint in pixels
    def draw_callback_2d(self, op, context):

        region = context.region
        xt = int(region.width / 2.0)

        # Draw text for draw mode
        blf_set_size(0, 22)
        blf.color(0, 1, 1, 1, 1)

        blf_set_size(1, 16)
        blf.color(1, 1, 1, 1, 1)

        title = "- Retopo Ring Mesh -"
        desc = "Ctrl + Click: Add points, Enter: Create, Ctrl + Enter: Create closed"

        blf.position(0, xt - blf.dimensions(0, title)[0] / 2, 45, 0)
        blf.draw(0, title)

        blf.position(1, xt - blf.dimensions(1, desc)[0] / 2, 20, 0)
        blf.draw(1, desc)
