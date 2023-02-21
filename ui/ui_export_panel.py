import bpy
import os
import xml.etree.ElementTree as xml

from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, IntProperty, BoolProperty, CollectionProperty, EnumProperty

from .ui_subject_panel import MK_SPRITES_action_item

from ..utils.xmlutils import GetMonoXMLHeader, XMLIndent, ExportXml
from ..utils.tileutils import GetTilePos
from ..operators.op_render_sprite_animation import get_action_frame_count
from ..operators.op_export_data_sheets import MK_SPRITES_OP_export_image_json, MK_SPRITES_OP_export_image_xml

def update_active_image(self, context):
    export_props = context.scene.mk_sprites_export_panel_properties

    if export_props.image == None:
        export_props.image_props[export_props.active_image].image = None
        return

    for image_prop in export_props.image_props:
        if image_prop.image == export_props.image:
            export_props.image_props[export_props.active_image].image = image_prop.image
            return

class MK_SPRITES_image_item(bpy.types.PropertyGroup):
    image: PointerProperty(
        type=bpy.types.Image,
        name='Image'
    )
    object_angles: IntProperty(
        name="Object Angles",
        default=0,
    )
    object_actions: CollectionProperty(
        type=MK_SPRITES_action_item,
        name='Actions'
    )
    sprite_width: IntProperty(
        name="sprite_width",
        default=32,
    )
    sprite_height: IntProperty(
        name="sprite_height",
        default=32,
    )

class MK_SPRITES_OP_export_image_data(bpy.types.Operator):
    """open_action_menu"""
    bl_idname = "mk_sprites.export_image_data"
    bl_label = "Export Sprite Sheet"

    # fileselect_add settings
    filename_ext = ""

    filter_glob: StringProperty(
        default="*.png",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    filepath: StringProperty(
        default=""
    )

    # UI members
    export_image: BoolProperty(
        name="Export Image",
        description="Example Tooltip",
        default=True,
    )
    export_json: BoolProperty(
        name="Export JSON",
        description="Example Tooltip",
        default=False,
    )
    export_xml: BoolProperty(
        name="Export XML",
        description="Example Tooltip",
        default=False,
    )
    export_mono: BoolProperty(
        name="Export XML for Monogame",
        description="Example Tooltip",
        default=False,
    )

    engine_presets : EnumProperty(
        name="Presets:",
        description="choose an engine",
        items=
        [
            ('Monogame', 'Monogame', "Export for Monogame/XNA content manager "),
            ('Generic', 'Generic', "Export without any engine specific data", 32)
        ],
        default='Generic'
    )

    # Temp members
    color_mode : EnumProperty(
        name="color_mode",
        items=
        [
            ('BW', 'BW', "BW"),
            ('RGB', 'RGB', "RGB"),
            ('RGBA', 'RGBA', "RGBA")
        ],
        default='BW'
    )
    color_depth: EnumProperty(
        name="color_depth",
        items=
        [
            ('8', '8', "8"),
            ('10', '10', "10"),
            ('12', '12', "12"),
            ('16', '16', "16"),
            ('32', '32', "32")
        ],
        default='8'
    )
    compression: IntProperty(
        name="compression",
        default=15,
    )
    exr_codec : EnumProperty(
        name="exr_codec",
        items=
        [
            ('NONE', 'NONE', "NONE"),
            ('PXR24', 'PXR24', "PXR24"),
            ('ZIP', 'ZIP', "ZIP"),
            ('PIZ', 'PIZ', "PIZ"),
            ('RLE', 'RLE', "RLE"),
            ('ZIPS', 'ZIPS', "ZIPS"),
            ('B44', 'B44', "B44"),
            ('B44A', 'B44A', "B44A"),
            ('DWAA', 'DWAA', "DWAA"),
            ('DWAB', 'DWAB', "DWAB"),
        ],
        default='NONE'
    )
    file_format : EnumProperty(
        name="file_format",
        items=
        [
            ('BMP', 'BMP', "BMP"),
            ('IRIS', 'IRIS', "IRIS"),
            ('PNG', 'PNG', "PNG"),
            ('JPEG', 'JPEG', "JPEG"),
            ('JPEG2000', 'JPEG2000', "JPEG2000"),
            ('TARGA', 'TARGA', "TARGA"),
            ('TARGA_RAW', 'TARGA_RAW', "TARGA_RAW"),
            ('CINEON', 'CINEON', "CINEON"),
            ('OPEN_EXR_MULTILAYER', 'OPEN_EXR_MULTILAYER', "OPEN_EXR_MULTILAYER"),
            ('OPEN_EXR', 'OPEN_EXR', "OPEN_EXR"),
            ('HDR', 'HDR', "HDR"),
            ('TIFF', 'TIFF', "TIFF"),
            ('WEBP', 'WEBP', "WEBP"),
        ],
        default='PNG'
    )
    jpeg2k_codec : EnumProperty(
        name="jpeg2k_codec",
        items=
        [
            ('JP2', 'JP2', "JP2"),
            ('J2K', 'J2K', "J2K"),
        ],
        default='JP2'
    )
    tiff_codec : EnumProperty(
        name="tiff_codec",
        items=
        [
            ('NONE', 'NONE', "NONE"),
            ('DEFLATE', 'DEFLATE', "DEFLATE"),
            ('LZW', 'LZW', "LZW"),
            ('PACKBITS', 'PACKBITS', "PACKBITS"),
        ],
        default='NONE'
    )
    use_jpeg2k_cinema_48: BoolProperty(
        name="use_jpeg2k_cinema_48",
        default=False,
    )
    use_jpeg2k_cinema_preset: BoolProperty(
        name="use_jpeg2k_cinema_preset",
        default=False,
    )
    use_jpeg2k_ycc: BoolProperty(
        name="use_jpeg2k_ycc",
        default=False,
    )
    use_zbuffer: IntProperty(
        name="use_zbuffer",
        default=0,
    )

    @classmethod
    def poll(self, context):
        export_props = context.scene.mk_sprites_export_panel_properties
        return export_props.image_props[export_props.active_image].image

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "export_image")
        if (self.export_image):
            col.template_image_settings(context.scene.render.image_settings, color_management=False)

        col.prop(self, "export_json")
        #col.prop(self, "export_asesprite json")

        col.prop(self, "export_xml")
        col.prop(self, "export_mono")

    def execute(self, context):
        export_props = context.scene.mk_sprites_export_panel_properties

        if not export_props.image_props[export_props.active_image]:
            return {'FINISHED'}

        if self.export_image:
            export_props.image_props[export_props.active_image].image.filepath_raw = self.filepath #os.path.join(self.filepath, "TEMP IMAGE NAME.png")
            export_props.image_props[export_props.active_image].image.save()
            pass

        if self.export_json:
            bpy.ops.mk_sprites.export_image_json(filepath = self.filepath)

        if self.export_xml or self.export_mono:
            bpy.ops.mk_sprites.export_image_xml(filepath = self.filepath, use_mono = self.export_mono)

        rs = context.scene.render.image_settings

        # reset scene settings
        rs.color_mode = self.color_mode
        rs.compression = self.compression
        rs.exr_codec = self.exr_codec
        rs.jpeg2k_codec = self.jpeg2k_codec
        rs.tiff_codec = self.tiff_codec
        rs.use_jpeg2k_cinema_48 = self.use_jpeg2k_cinema_48
        rs.use_jpeg2k_cinema_preset = self.use_jpeg2k_cinema_preset
        rs.use_jpeg2k_ycc = self.use_jpeg2k_ycc
        rs.use_zbuffer = self.use_zbuffer
        rs.color_depth = self.color_depth
        rs.file_format = self.file_format

        return {'FINISHED'}

    def invoke(self, context, event):
        mk_export_props = context.scene.mk_sprites_export_panel_properties
        rs = context.scene.render.image_settings

        # temp
        self.color_mode = rs.color_mode
        self.compression = rs.compression
        self.exr_codec = rs.exr_codec
        self.jpeg2k_codec = rs.jpeg2k_codec
        self.tiff_codec = rs.tiff_codec
        self.use_jpeg2k_cinema_48 = rs.use_jpeg2k_cinema_48
        self.use_jpeg2k_cinema_preset = rs.use_jpeg2k_cinema_preset
        self.use_jpeg2k_ycc = rs.use_jpeg2k_ycc
        self.use_zbuffer = rs.use_zbuffer
        self.color_depth = rs.color_depth
        self.file_format = rs.file_format

        img_path = os.path.splitext(mk_export_props.image.filepath)
        img_name = img_path[0]
        img_ext = img_path[1]

        if (img_name == ""):
            img_name = mk_export_props.image.name

        if (img_ext == None or img_ext == "" ):
            self.filename_ext = str.lower(rs.file_format)
            self.filepath = img_name + "." + self.filename_ext

        else:
            self.filename_ext = img_ext
            self.filepath = mk_export_props.image.filepath
            rs.file_format = str.upper(img_ext[1:])

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MK_SPRITES_PT_export_panel_properties(bpy.types.PropertyGroup):
    image: PointerProperty(
        type=bpy.types.Image,
        name='Image',
        update = update_active_image
    )

    active_image: IntProperty(
        name="Active Image",
        default=0
    )

    image_props: CollectionProperty(
        type=MK_SPRITES_image_item,
        name='Images'
    )

    def register():
        bpy.types.Scene.mk_sprites_export_panel_properties = PointerProperty(type=MK_SPRITES_PT_export_panel_properties)

    def unregister():
        del bpy.types.Scene.mk_sprites_export_panel_properties

class MK_SPRITES_PT_export_panel(bpy.types.Panel):
    bl_idname = "MK_SPRITES_PT_export_panel"
    bl_label = "Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sprites'

    def draw(self, context):
        layout = self.layout
        export_props = context.scene.mk_sprites_export_panel_properties

        column = layout.column(align=True)
        column.prop(export_props, "image")

        layout.separator()
        col = layout.column()
        col.operator("mk_sprites.export_image_data")