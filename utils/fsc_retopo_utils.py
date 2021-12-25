from . fsc_common_utils import get_axis_no

def add_mirror(retopo_object, context):
  mod_mirror = retopo_object.modifiers.new(type="MIRROR", name="FSC_MIRROR")
  mod_mirror.use_axis[0] = False
  mod_mirror.use_axis[get_axis_no(context.scene.add_retopo_mirror)] = True
  mod_mirror.use_clip = True
  mod_mirror.merge_threshold = 0.01
  mod_mirror.show_on_cage = True


def add_shrinkwrap(retopo_object, context):
  mod_sw = retopo_object.modifiers.new(type="SHRINKWRAP", name="FSC_SHRINKWRAP")
  mod_sw.target = context.scene.retopo_object
  mod_sw.wrap_mode = 'ABOVE_SURFACE'
  mod_sw.offset = 0.03

def set_retopo_settings(context):
  my_areas = context.workspace.screens[0].areas

  for area in my_areas:
      for space in area.spaces:
          if space.type == 'VIEW_3D':
              space.shading.show_backface_culling = True

  context.scene.tool_settings.snap_elements = {'FACE'}
  context.scene.tool_settings.use_snap_project = True
  context.scene.tool_settings.use_snap = True