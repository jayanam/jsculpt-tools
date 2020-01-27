bl_info = {
    "name" : "JSculpt Tools",
    "author" : "jayanam",
    "description" : "Sculpting tools for Blender 2.8",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Object"
}

import bpy
from bpy.props import *

from . fsc_panel import *
from . fsc_bool_op import *
from . fsc_mask_op import *
from . fsc_remesh_op import *
from . fsc_retopo_op import *
from . fsc_add_object_op import *

# Global properties
bpy.types.WindowManager.in_add_mode = BoolProperty(name="Add Mode",
                                        default = False)

# Scene properties
bpy.types.Scene.target_object = PointerProperty(type=bpy.types.Object)

bpy.types.Scene.retopo_object = PointerProperty(type=bpy.types.Object)

bpy.types.Scene.extract_thickness = bpy.props.FloatProperty( name="Extract thickness", 
                                      description="Thickness of the extracted mesh",
                                      default = 0.1)

bpy.types.Scene.extract_offset = bpy.props.FloatProperty( name="Extract offset", 
                                      description="Offset of the extracted mesh",
                                      default = 0.0)

bpy.types.Scene.remesh_voxel_size = bpy.props.FloatProperty( name="Remesh voxel size", 
                                      description="Voxel size of remesh",
                                      default = 0.01, 
                                      min = 0.0,
                                      precision=4)

bpy.types.Scene.align_to_face  = BoolProperty(name="Align to face", 
                                      description="Align to face orientation",
                                      default = True)

bpy.types.Scene.remesh_smooth_normals  = BoolProperty(name="Smooth normals", 
                                      description="Smooth normals after remesh",
                                      default = False)

bpy.types.Scene.remesh_fix_poles  = BoolProperty(name="Fix poles", 
                                      description="Fix the poles",
                                      default = False)

bpy.types.Scene.remesh_preserve_volume = BoolProperty(name="Preserve volume", 
                                      description="Try to preserve the volume",
                                      default = True)

bpy.types.Scene.remesh_after_extract  = BoolProperty(name="Remesh after extract", 
                                      description="Remesh the mesh after mask extraction",
                                      default = True)

bpy.types.Scene.remesh_after_union  = BoolProperty(name="Remesh after union", 
                                      description="Remesh the mesh after union operation",
                                      default = True)

add_object_types = [ ("Sphere",    "Sphere",   "", 0),
                     ("Plane",     "Plane",    "", 1),
                     ("Cube",      "Cube",     "", 2),
                     ("Cylinder",  "Cylinder", "", 3),
                     ("Torus",     "Torus",    "", 4),
                     ("Cone",      "Cone",     "", 5),
                     ("Icosphere", "Icosphere","", 6),
                     ("Scene",     "Scene",    "", 7),      
                  ]

add_object_mirror = [("None",    "None",  "", 0),
                     ("X",       "X",     "", 1),
                     ("Y",       "Y",     "", 2),
                     ("Z",       "Z",     "", 3)    
                  ]

bpy.types.Scene.add_object_type = bpy.props.EnumProperty(items=add_object_types, 
                                                        name="Add Object",
                                                        default="Sphere")

bpy.types.Scene.add_object_mirror = bpy.props.EnumProperty(items=add_object_mirror, 
                                                        name="Add Object Mirror",
                                                        default="None")                                                

bpy.types.Scene.add_scene_object = PointerProperty(type=bpy.types.Object)

addon_keymaps = []

classes = ( FSC_PT_Panel, FSC_PT_Bool_Objects_Panel, FSC_PT_Add_Objects_Panel, FSC_PT_Extract_Mask_Panel, 
            FSC_PT_Remesh_Panel, FSC_PT_Retopo_Panel, FSC_OT_BoolOperator_Union, 
            FSC_OT_BoolOperator_Difference, FSC_OT_Mask_Extract_Operator, 
            FSC_OT_Remesh_Operator, FSC_OT_Add_Oject_Operator, FSC_OT_Retopo_Operator )

def register():
    for c in classes:
        bpy.utils.register_class(c)

    # add keymap entry
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

    kmi = km.keymap_items.new("object.fsc_add_object", 'A', 'PRESS', shift=True, ctrl=True)
    addon_keymaps.append((km, kmi))

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    # remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()
    
if __name__ == "__main__":
    register()
