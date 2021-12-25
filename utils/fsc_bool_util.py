import bpy
from bpy.props import *

import bmesh

from .fsc_select_mode_utils import *

def check_cutter_selected(context):
    result = len(context.selected_objects) > 0
    result = result and not bpy.context.scene.target_object is None
    result = result and not (bpy.context.scene.target_object == bpy.context.view_layer.objects.active)
    return result

def select_active(obj):

    deselect_all()
    
    make_active(obj)

def recalc_normals(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.clear()
    mesh.update()
    bm.free()
    
def bool_mod_and_apply(obj, bool_method, delete_selected = True):
    
    active_obj = bpy.context.active_object
    
    bool_mod = active_obj.modifiers.new(type="BOOLEAN", name="FSC_BOOL")
    
    method = 'DIFFERENCE'
    
    if bool_method == 1:
        method = 'UNION'
    
    bool_mod.operation = method
    bool_mod.object = obj

    recalc_normals(obj.data)
    
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)

    if delete_selected:
        select_active(obj)
        bpy.ops.object.delete()

def execute_remesh(context):
    bpy.context.object.data.use_remesh_preserve_volume = context.scene.remesh_preserve_volume
    bpy.context.object.data.use_remesh_fix_poles = context.scene.remesh_fix_poles
    bpy.context.object.data.remesh_voxel_size = context.scene.remesh_voxel_size
    bpy.ops.object.voxel_remesh()

def execute_boolean_op(context, target_obj, bool_method = 0, delete_selected = True):
    
    current_obj = context.object
    make_active(current_obj)
    to_object()
    bpy.ops.object.transform_apply(scale=True)

    make_active(target_obj)
    to_object()
    bpy.ops.object.transform_apply(scale=True)
  
    bool_mod_and_apply(current_obj, bool_method, delete_selected)

    make_active(target_obj)
    to_sculpt()

    if context.scene.remesh_after_union:
        execute_remesh(context)

    # difference operation
    if bool_method == 0:
        to_object()
        select_active(current_obj)