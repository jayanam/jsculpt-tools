import bpy

from bpy.props import *

from bpy.types import AddonPreferences

def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences

class FSC_AddonPreferences(AddonPreferences):
    bl_idname = __package__

    keyboard_section : BoolProperty(
        name="Keyboard Shortcuts",
        description="Keyboard Shortcuts",
        default=True
    )

    def add_key_item_row(self, item):
        row = self.layout.row()
        row.label(text=item.name)
        row.prop(item, 'type', text='', full_event=True)

   
    def draw(self, context):
        
        wm = bpy.context.window_manager 

        layout = self.layout

        # Keyboard shortcuts section
        layout.prop(self, "keyboard_section", icon='DISCLOSURE_TRI_DOWN' if self.keyboard_section else 'DISCLOSURE_TRI_RIGHT')
        if self.keyboard_section:

            km_items = wm.keyconfigs.user.keymaps['3D View'].keymap_items         

            self.add_key_item_row(km_items['object.fsc_add_object'])

            if bpy.app.version >= (3, 0, 0):
                self.add_key_item_row(km_items['object.fsc_select_object'])