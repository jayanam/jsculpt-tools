import bpy

from bpy_extras.view3d_utils import (
    region_2d_to_origin_3d,
    region_2d_to_vector_3d,
    region_2d_to_location_3d
)

import mathutils

def get_3d_for_2d(pos_2d, context):

    result = None, None

    scene = context.scene

    origin, direction = get_origin_and_direction(pos_2d, context)

    # Try to hit an object in the scene
    ray_cast_param = __get_raycast_param(context.view_layer)
    hit, hit_vertex, normal, hit_face, hit_obj, *_ = scene.ray_cast(ray_cast_param, origin, direction)

    if hit:
        result = hit_vertex.copy(), hit_obj
        
    return result

def get_view_rotation(context):
    rv3d      = context.space_data.region_3d
    view_rot  = rv3d.view_rotation
    return view_rot 

def get_view_direction(context):
    view_rot  = get_view_rotation(context)
    
    dir = view_rot @ mathutils.Vector((0,0,-1))

    return dir.normalized()

def get_3d_vertex(context, vertex_2d):
    region    = context.region
    rv3d      = context.space_data.region_3d

    dir = get_view_direction(context) * -1
    
    return region_2d_to_location_3d(region, rv3d, vertex_2d, dir)   

def __get_raycast_param(view_layer):        
    if bpy.app.version >= (2, 91, 0):
        return view_layer.depsgraph
    else:
        return view_layer 

def get_origin_and_direction(pos_2d, context):
    region    = context.region
    region_3d = context.space_data.region_3d
    
    origin    = region_2d_to_origin_3d(region, region_3d, pos_2d)
    direction = region_2d_to_vector_3d(region, region_3d, pos_2d)

    return origin, direction

def scene_raycast(direction, origin, context):

    scene = context.scene

    # Try to hit an object in the scene
    ray_cast_param = __get_raycast_param(context.view_layer)
    hit, hit_vertex, normal, hit_face, hit_obj, *_ = scene.ray_cast(ray_cast_param, origin, direction)
    return hit, hit_vertex

def get_center_vectors(v1 : mathutils.Vector, v2 : mathutils.Vector):
    return (v2 + v1) / 2