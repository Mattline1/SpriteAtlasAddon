import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, IntProperty, BoolProperty, EnumProperty
from bpy.app.translations import pgettext_tip as tip_
from ..utils.xmlutils import ExportXml

def update_default_render_size(self, context):
    context.scene.mk_sprites_render_panel_properties.resolution_x = int(self.resolution_presets)
    context.scene.mk_sprites_render_panel_properties.resolution_y = int(self.resolution_presets)

class MK_SPRITES_PT_render_panel_properties(bpy.types.PropertyGroup):
    resolution_presets : EnumProperty(
        name="Presets:",
        description="choose a common sprite size",
        items=
        [
            ('16', '16x16', "Flat geometry", 16),
            ('32', '32x32', "Use z value from shape geometry if exists", 32),
            ('50', '50x50', "Use z value from shape geometry if exists", 50),
            ('64', '64x64', "Extract z elevation value from an attribute field", 64),
            ('128', '128x128', "Get z elevation value from an existing ground mesh", 128)
        ],
        update = update_default_render_size,
        default='32'
        )

    resolution_x: IntProperty(
        name="resolution_x",
        default= 32
    )
    resolution_y: IntProperty(
        name="resolution y",
        default= 32
    )
    auto_resolution: BoolProperty(
        name="auto",
        default=True
    )
    image_resolution_x: IntProperty(
        name="resolution_x",
        default=256
    )
    image_resolution_y: IntProperty(
        name="resolution y",
        default=256
    )

    def register():
        bpy.types.Scene.mk_sprites_render_panel_properties = PointerProperty(type=MK_SPRITES_PT_render_panel_properties)

    def unregister():
        del bpy.types.Scene.mk_sprites_render_panel_properties

# panel for output options
class MK_SPRITES_PT_render_panel(bpy.types.Panel):
    bl_idname = "MK_SPRITES_PT_render_panel"
    bl_label = "Info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sprites'

    _frame_rate_args_prev = None
    _preset_class = None

    @staticmethod
    def _draw_framerate_label(*args):
        # avoids re-creating text string each draw
        if MK_SPRITES_PT_render_panel._frame_rate_args_prev == args:
            return MK_SPRITES_PT_render_panel._frame_rate_ret

        fps, fps_base, preset_label = args

        if fps_base == 1.0:
            fps_rate = round(fps)
        else:
            fps_rate = round(fps / fps_base, 2)

        custom_framerate = (fps_rate not in {23.98, 24, 25, 29.97, 30, 50, 59.94, 60, 120, 240})

        if custom_framerate is True:
            fps_label_text = tip_("Custom (%.4g fps)") % fps_rate
            show_framerate = True
        else:
            fps_label_text = tip_("%.4g fps") % fps_rate
            show_framerate = (preset_label == "Custom")

        MK_SPRITES_PT_render_panel._frame_rate_args_prev = args
        MK_SPRITES_PT_render_panel._frame_rate_ret = args = (fps_label_text, show_framerate)
        return args

    @staticmethod
    def draw_framerate(layout, rd):
        if MK_SPRITES_PT_render_panel._preset_class is None:
            MK_SPRITES_PT_render_panel._preset_class = bpy.types.RENDER_MT_framerate_presets

        args = rd.fps, rd.fps_base, MK_SPRITES_PT_render_panel._preset_class.bl_label
        fps_label_text, show_framerate = MK_SPRITES_PT_render_panel._draw_framerate_label(*args)

        layout.menu("RENDER_MT_framerate_presets", text=fps_label_text)

        if show_framerate:
            col = layout.column(align=True)
            col.prop(rd, "fps")
            col.prop(rd, "fps_base", text="Base")

    def draw(self, context):
        subject_props = context.scene.mk_sprites_subject_panel_properties
        render_props = context.scene.mk_sprites_render_panel_properties

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        rd = context.scene.render
        col = layout.column(align=True)

        col.prop(render_props, "resolution_x", text="Resolution X")
        col.prop(render_props, "resolution_y", text="Y")

        col = layout.column(align=True)
        col.prop(render_props, "resolution_presets")

        col.prop(render_props, "auto_resolution")
        sub = col.column(align=True)
        sub.enabled = not render_props.auto_resolution
        sub.prop(render_props, "image_resolution_x", text="ImageSize X")
        sub.prop(render_props, "image_resolution_y", text="Y")

        col = layout.column(heading="Frame Rate")
        self.draw_framerate(col, rd)

        op = col.operator("mk_sprites.render_sprite_animation")
        op.subject_rotations = subject_props.rotations
        op.use_animations = len(subject_props.obj_actions) > 0