import bpy

from bpy_extras.view3d_utils import (
    region_2d_to_origin_3d,
    region_2d_to_vector_3d
)

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