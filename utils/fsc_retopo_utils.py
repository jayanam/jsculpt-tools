import bpy

from . fsc_common_utils import get_axis_no

def add_mirror(retopo_object, context):
  mod_mirror = retopo_object.modifiers.new(type="MIRROR", name="FSC_MIRROR")
  mod_mirror.use_axis[0] = False
  mod_mirror.use_axis[get_axis_no(context.scene.add_retopo_mirror)] = True
  mod_mirror.use_clip = True
  mod_mirror.merge_threshold = 0.01
  mod_mirror.show_on_cage = True


def get_modifier(object, type):
  for mod in object.modifiers:
    if mod.type == type:
      return mod
  return None

def add_solidify(retopo_object, context):
  mod_solid = get_modifier(retopo_object, "SOLIDIFY")
  if not mod_solid:
    mod_solid = retopo_object.modifiers.new(type="SOLIDIFY", name="FSC_SOLIDIFY")
    mod_solid.use_even_offset = True

  return mod_solid

def add_subsurf(retopo_object, context):
  mod_subsurf = get_modifier(retopo_object, "SUBSURF")
  if not mod_subsurf:
    mod_subsurf = retopo_object.modifiers.new(type="SUBSURF", name="FSC_SUBSURF")
    bpy.ops.object.modifier_move_to_index(modifier=mod_subsurf.name, index=0)

  return mod_subsurf

def add_shrinkwrap(retopo_object, context):
  mod_sw = get_modifier(retopo_object, "SHRINKWRAP")
  if not mod_sw:
    mod_sw = retopo_object.modifiers.new(type="SHRINKWRAP", name="FSC_SHRINKWRAP")
    mod_sw.target = context.scene.retopo_object
    mod_sw.wrap_mode = 'ABOVE_SURFACE'
    mod_sw.offset = 0.02
    mod_sw.show_on_cage = True
  return mod_sw

def set_retopo_settings(context):
  my_areas = context.workspace.screens[0].areas

  for area in my_areas:
      for space in area.spaces:
          if space.type == 'VIEW_3D':
              space.shading.show_backface_culling = True

  context.scene.tool_settings.snap_elements = {'FACE'}
  context.scene.tool_settings.use_snap_project = True
  context.scene.tool_settings.use_snap = True