import bpy
from bpy.types import PropertyGroup, ID
from bpy.props import PointerProperty, StringProperty, IntProperty, BoolProperty, CollectionProperty
from ..utils.xmlutils import ExportXml

class MK_SPRITES_action_item(bpy.types.PropertyGroup):
    action: PointerProperty(
        type=bpy.types.Action,
        name='Action'
    )

class MK_SPRITES_PT_subject_panel_properties(bpy.types.PropertyGroup):
    rotations: IntProperty(
        name='Object Rotations',
        default=4
    )
    obj: PointerProperty(
        type=bpy.types.Object,
        name='Object'
    )
    active_action: IntProperty(
        name='Active'
    )
    obj_actions: CollectionProperty(
        type=MK_SPRITES_action_item,
        name='Actions'
    )

    def register():
        bpy.types.Scene.mk_sprites_subject_panel_properties = PointerProperty(type=MK_SPRITES_PT_subject_panel_properties)

    def unregister():
        del bpy.types.Scene.mk_sprites_subject_panel_properties

class MK_SPRITES_OP_sprite_action_add(bpy.types.Operator):
    """open_action_menu"""
    bl_idname = "mk_sprites.sprite_action_add"
    bl_label = "Add Action"
    bl_options = {'REGISTER'}

    def execute(self, context):
        panel_props = context.scene.mk_sprites_subject_panel_properties
        panel_props.obj_actions.add()

        return {'FINISHED'}

class MK_SPRITES_OP_sprite_action_remove(bpy.types.Operator):
    """open_action_menu"""
    bl_idname = "mk_sprites.sprite_action_remove"
    bl_label = "Remove Action"
    bl_options = {'REGISTER'}

    def execute(self, context):
        panel_props = context.scene.mk_sprites_subject_panel_properties
        panel_props.obj_actions.remove(panel_props.active_action)
        return {'FINISHED'}

class MK_SPRITES_OP_sprite_action_new(bpy.types.Operator):
    """open_action_menu"""
    bl_idname = "mk_sprites.sprite_action_new"
    bl_label = "Add Action"
    bl_options = {'REGISTER'}

    def execute(self, context):
        panel_props = context.scene.mk_sprites_subject_panel_properties
        action_item = panel_props.obj_actions[panel_props.active_action]
        action_item.action = context.blend_data.actions.new("Action")
        return {'FINISHED'}

class MK_SPRITES_UL_action_item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item and item.action:
                layout.prop(item.action, "name", text="", emboss=False, icon = "ACTION")
            else:
                layout.label(text="", translate=False, icon = "ACTION", icon_value = icon)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class MK_SPRITES_PT_subject_panel(bpy.types.Panel):
    bl_idname = "MK_SPRITES_PT_subject_panel"
    bl_label = "Subject"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sprites'

    def draw(self, context):
        layout = self.layout
        panel_props = context.scene.mk_sprites_subject_panel_properties

        layout.prop(panel_props, "obj")

        if panel_props.obj:
            layout.prop(panel_props, "rotations")

            layout.label(text="Actions:")
            row = layout.row()
            row.template_list("MK_SPRITES_UL_action_item", "", panel_props, "obj_actions", panel_props, "active_action")

            col = row.column(align=True)
            col.operator("mk_sprites.sprite_action_add", icon='ADD', text="")
            col.operator("mk_sprites.sprite_action_remove", icon='REMOVE', text="")

            if (len(panel_props.obj_actions) > 0):
                row2 = layout.row()
                row2.template_ID(panel_props.obj_actions[panel_props.active_action], "action", new="mk_sprites.sprite_action_new", unlink="mk_sprites.sprite_action_remove")