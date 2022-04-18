bl_info = {
    "name" : "JSculpt Tools",
    "author" : "jayanam",
    "description" : "Sculpting tools for Blender 2.8 - 3.x",
    "blender" : (2, 80, 0),
    "version" : (1, 3, 1, 0),
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
from . fsc_add_object_op import *
from . fsc_select_op import *
from . fsc_preferences import FSC_AddonPreferences
from . fsc_draw_mode_op import *
from . fsc_subsurf_op import *
from . fsc_shrinkwrap_op import *
from . fsc_solidify_op import *
from . fsc_apply_op import *
from . fsc_retopo_ring_op import *

# Global properties
bpy.types.WindowManager.in_modal_mode = BoolProperty(name="Modal Mode",
                                        default = False)

add_object_mirror = [("None",    "None",  "", 0),
                     ("X",       "X",     "", 1),
                     ("Y",       "Y",     "", 2),
                     ("Z",       "Z",     "", 3)    
                  ]

# Scene properties
bpy.types.Scene.target_object = PointerProperty(type=bpy.types.Object)

bpy.types.Scene.retopo_object = PointerProperty(type=bpy.types.Object)

bpy.types.Scene.retopo_mesh = PointerProperty(type=bpy.types.Object)

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

bpy.types.Scene.remesh_fix_poles  = BoolProperty(name="Fix poles", 
                                      description="Fix the poles",
                                      default = False)

bpy.types.Scene.remesh_preserve_volume = BoolProperty(name="Preserve volume", 
                                      description="Try to preserve the volume",
                                      default = True)

bpy.types.Scene.remesh_after_extract  = BoolProperty(name="Remesh after extract", 
                                      description="Remesh the mesh after mask extraction",
                                      default = True)

bpy.types.Scene.add_retopo_mirror = bpy.props.EnumProperty(items=add_object_mirror, 
                                                        name="Retopo Mirror",
                                                        default="None") 

add_object_types = [ ("Sphere",    "Sphere",   "", 0),
                     ("Plane",     "Plane",    "", 1),
                     ("Cube",      "Cube",     "", 2),
                     ("Cylinder",  "Cylinder", "", 3),
                     ("Torus",     "Torus",    "", 4),
                     ("Cone",      "Cone",     "", 5),
                     ("Icosphere", "Icosphere","", 6),
                     ("Scene",     "Scene",    "", 7),      
                  ]

# Scene properties
bpy.types.WindowManager.in_draw_mode = BoolProperty(name="Draw Mode", default = False)

bpy.types.Scene.add_object_type = bpy.props.EnumProperty(items=add_object_types, 
                                                        name="Add Object",
                                                        default="Sphere")

bpy.types.Scene.add_object_mirror = bpy.props.EnumProperty(items=add_object_mirror, 
                                                        name="Add Object Mirror",
                                                        default="None")                                                

bpy.types.Scene.add_scene_object = PointerProperty(type=bpy.types.Object)

addon_keymaps = []

classes = ( FSC_PT_Panel, FSC_PT_Add_Objects_Panel, FSC_PT_Extract_Mask_Panel, 
            FSC_PT_Remesh_Panel, FSC_PT_Retopo_Panel, FSC_OT_BoolOperator_Union, 
            FSC_OT_BoolOperator_Difference, FSC_OT_Mask_Extract_Operator, FSC_OT_Mask_Invert_Transform_Operator,
            FSC_OT_Remesh_Operator, FSC_OT_Add_Oject_Operator, FSC_OT_Select_Operator,
            FSC_AddonPreferences, FSC_OT_Draw_Mode_Operator, FSC_OT_Subsurf_Operator, FSC_OT_Shrinkwrap_Operator,
            FSC_OT_Solidify_Operator, FSC_OT_FlipNormals_Operator, FSC_OT_ApplyAllModifiersOperator,
            FSC_OT_Retopo_Ring_Operator)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    # add keymap entry
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

    kmi = km.keymap_items.new("object.fsc_add_object", 'A', 'PRESS', shift=True, ctrl=True)
    addon_keymaps.append((km, kmi))

    if bpy.app.version >= (3, 0, 0):
        kmi = km.keymap_items.new("object.fsc_select_object", 'D', 'PRESS', shift=True, ctrl=False)
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
