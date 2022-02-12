import bpy
from bpy.types import Operator
from bpy_extras import object_utils

from . utils.fsc_retopo_utils import add_shrinkwrap, get_modifier

from . utils.fsc_select_mode_utils import *

from .utils.fsc_unit_utils import *

from .widgets . bl_ui_draw_op import *
from .widgets . bl_ui_label import * 
from .widgets . bl_ui_button import *
from .widgets . bl_ui_textbox import *
from .widgets . bl_ui_drag_panel import *
from .widgets . bl_ui_draw_op import *

class FSC_OT_Shrinkwrap_Operator(BL_UI_OT_draw_operator):
    bl_idname = "object.fsc_shrinkwrap"
    bl_label = ""
    bl_description = "Add Shrinkwrap Modifier if not exists" 
    bl_options = {'REGISTER', 'UNDO'} 

    @classmethod
    def poll(cls, context):
        return context.view_layer.objects.active is not None

    def __init__(self):

        y_top = 35
        x_left = 100

        super().__init__()
        self.panel = BL_UI_Drag_Panel(0, 0, 280, 120)
        self.panel.bg_color = (0.1, 0.1, 0.1, 0.9)

        self.lbl_width = BL_UI_Label(20, y_top, 50, 15)
        self.lbl_width.text = "Offset:"
        self.lbl_width.text_size = 14
        self.lbl_width.text_color = (0.9, 0.9, 0.9, 1.0)

        unitinfo = get_current_units()
        self.offset = BL_UI_Textbox(x_left, y_top - 2, 125, 24)
        self.offset.max_input_chars = 8
        self.offset.is_numeric = True
        self.offset.label = unitinfo[0]
        input_keys = self.offset.get_input_keys()
        input_keys.remove('RET')
        input_keys.remove('ESC')
        self.offset.set_text_changed(self.on_input_changed)

        self.lbl_close = BL_UI_Label(195, y_top - 35, 50, 15)
        self.lbl_close.text = "Escape to Close"
        self.lbl_close.text_size = 10
        self.lbl_close.text_color = (0.9, 0.9, 0.9, 1.0)

        self.btn_apply = BL_UI_Button(20, y_top + 45, 110, 25)
        self.btn_apply.bg_color = (0.3, 0.56, 0.94, 1.0)
        self.btn_apply.hover_bg_color = (0.3, 0.56, 0.94, 0.8)
        self.btn_apply.text_size = 14
        self.btn_apply.text = "Apply modifier"
        self.btn_apply.set_mouse_down(self.on_btn_apply_down)

        self.btn_close = BL_UI_Button(140, y_top + 45, 120, 25)
        self.btn_close.bg_color = (0.3, 0.56, 0.94, 1.0)
        self.btn_close.hover_bg_color = (0.3, 0.56, 0.94, 0.8)
        self.btn_close.text_size = 14
        self.btn_close.text = "Close"
        self.btn_close.set_mouse_down(self.on_btn_close_down)

    def on_btn_close_down(self, widget):
        self.finish()

    def on_btn_apply_down(self, widget):
      active_obj = bpy.context.view_layer.objects.active
      mod_shrinkwrap = get_modifier(active_obj, "SHRINKWRAP")

      if mod_shrinkwrap:
        bpy.ops.object.modifier_apply(modifier=mod_shrinkwrap.name) 

      self.finish()

    def get_offset(self):
        value = float(self.offset.text)
        unitinfo = get_current_units()
        return unit_to_bu(value, unitinfo[1])

    def on_input_changed(self, textbox, context, event):
      active_obj = bpy.context.view_layer.objects.active

      mod_shrinkwrap = get_modifier(active_obj, "SHRINKWRAP")
      if mod_shrinkwrap is not None:
        mod_shrinkwrap.offset = self.get_offset()

    def on_finish(self, context):
        super().on_finish(context)


    def on_invoke(self, context, event):
        active_obj = context.view_layer.objects.active
        mod_shrinkwrap = add_shrinkwrap(active_obj, context)
        # Add new widgets here
        widgets_panel = [self.lbl_width, self.offset, self.lbl_close]
        widgets_panel.append(self.btn_apply)
        widgets_panel.append(self.btn_close)

        widgets = [self.panel]
        widgets += widgets_panel

        self.init_widgets(context, widgets)

        self.panel.add_widgets(widgets_panel)

        # Open the panel at the mouse location
        self.panel.set_location(context.area.height / 2.0, 
                                context.area.height / 2.0)

        self.init_widget_values()

    def init_widget_values(self):
        active_obj = bpy.context.view_layer.objects.active
        mod_shrinkwrap = get_modifier(active_obj, "SHRINKWRAP")
        if mod_shrinkwrap is not None:
            unitinfo = get_current_units()
            unit_value = bu_to_unit(mod_shrinkwrap.offset, unitinfo[1])
            self.offset.text  = "{:.2f}".format(unit_value)
