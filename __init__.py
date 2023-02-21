import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty
from . operators import op_render_sprite_animation, op_export_data_sheets
from . ui import ui_export_panel, ui_render_panel, ui_subject_panel

bl_info = {
    "name": "Sprite Atlas Tools",
    "author": "Martin Kearl",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "location": "View3D > UI > Sprites",
    "description": "Tools for rendering and exporting sprite sheets",
    "warning": "",
    "doc_url": "https://github.com/Mattline1/SpriteAtlasAddon",
    "category": "Export",
}

classes = (
    op_render_sprite_animation.MK_SPRITES_OP_render_sprite_animation,
    op_export_data_sheets.MK_SPRITES_OP_export_image_json,
    op_export_data_sheets.MK_SPRITES_OP_export_image_xml,
    ui_subject_panel.MK_SPRITES_OP_sprite_action_add,
    ui_subject_panel.MK_SPRITES_OP_sprite_action_remove,
    ui_subject_panel.MK_SPRITES_OP_sprite_action_new,
    ui_subject_panel.MK_SPRITES_action_item,
    ui_subject_panel.MK_SPRITES_UL_action_item,
    ui_subject_panel.MK_SPRITES_PT_subject_panel_properties,
    ui_subject_panel.MK_SPRITES_PT_subject_panel,
    ui_render_panel.MK_SPRITES_PT_render_panel_properties,
    ui_render_panel.MK_SPRITES_PT_render_panel,
    ui_export_panel.MK_SPRITES_image_item,
    ui_export_panel.MK_SPRITES_PT_export_panel_properties,
    ui_export_panel.MK_SPRITES_OP_export_image_data,
    ui_export_panel.MK_SPRITES_PT_export_panel
    )

def register():
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
    except:
        for cls in reversed(classes):
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass

if __name__ == "__main__":
    register()