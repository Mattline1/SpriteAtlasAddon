import bpy
import os
import xml.etree.ElementTree as xml
import json

from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, IntProperty, BoolProperty, CollectionProperty, EnumProperty

from ..utils.xmlutils import GetMonoXMLHeader, GetXMLHeader, XMLIndent, ExportXml
from ..utils.tileutils import GetTilePos
from ..operators.op_render_sprite_animation import get_action_frame_count

def make_mono_source(width, height, pos_x, pos_y):
    return str(pos_x) + " " + str(pos_y) + " " + str(width) + " " + str(height)

class MK_SPRITES_OP_export_image_json(bpy.types.Operator):
    """open_action_menu"""
    bl_idname = "mk_sprites.export_image_json"
    bl_label = "Add Action"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(name="filepath")

    def execute(self, context):
        mk_render_props = context.scene.mk_sprites_render_panel_properties
        export_props = context.scene.mk_sprites_export_panel_properties
        active_image = export_props.image_props[export_props.active_image]

        if active_image.image == None:
            return {'FINISHED'}

        image_width = active_image.image.size[0]
        image_height = active_image.image.size[1]

        n = 0
        items = []
        for obj_rot in range(active_image.object_angles):
            for action_obj in active_image.object_actions:
                if (action_obj == None or action_obj.action == None):
                    continue

                item = {}
                item["frames"] = get_action_frame_count(action_obj.action)
                item["framerate"] = context.scene.render.fps
                item["loop"] = True
                item["name"] = action_obj.action.name + "_" + str(obj_rot)
                item["width"] = mk_render_props.resolution_x
                item["height"] = mk_render_props.resolution_y
                posX, posY = GetTilePos(mk_render_props.resolution_x, mk_render_props.resolution_y, image_width, image_height, n)
                item["source_x"] = str(posX)
                item["source_y"] = str(posY)
                item["texture"] = os.path.basename(self.filepath)

                items.append(item)
                n += 1

        img_path = os.path.splitext(self.filepath)

        f = open(img_path[0] + ".json", 'w')
        f.write(json.dumps(items, indent=2, sort_keys=True))
        f.close()

        return {'FINISHED'}

class MK_SPRITES_OP_export_image_xml(bpy.types.Operator):
    """open_action_menu"""
    bl_idname = "mk_sprites.export_image_xml"
    bl_label = "Add Action"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(name="filepath")
    use_mono: bpy.props.BoolProperty(name="use_mono")

    def execute(self, context):
        mk_render_props = context.scene.mk_sprites_render_panel_properties
        export_props = context.scene.mk_sprites_export_panel_properties
        active_image = export_props.image_props[export_props.active_image]

        # start tree
        if self.use_mono:
            root, asset = GetMonoXMLHeader("animation")
        else:
            root, asset = GetXMLHeader()

        animations = xml.SubElement(asset, "animations")

        if active_image.image == None:
            return {'FINISHED'}

        image_width = active_image.image.size[0]
        image_height = active_image.image.size[1]
        n = 0

        for obj_rot in range(active_image.object_angles):
            for action_obj in active_image.object_actions:

                print(action_obj.action)
                if (action_obj == None or action_obj.action == None):
                    continue

                item = xml.SubElement(animations, "Item")

                xml.SubElement(item, "frames").text = str(get_action_frame_count(action_obj.action))
                xml.SubElement(item, "framerate").text = str(context.scene.render.fps)
                xml.SubElement(item, "loop").text = "True"
                xml.SubElement(item, "name").text = action_obj.action.name + "_" + str(obj_rot)

                width = mk_render_props.resolution_x
                height = mk_render_props.resolution_y
                posX, posY = GetTilePos(width, height, image_width, image_height, n)

                if self.use_mono:
                    xml.SubElement(item, "source").text = make_mono_source(width, height, posX, posY)
                else:
                    xml.SubElement(item, "width").text = str(width)
                    xml.SubElement(item, "height").text = str(height)
                    xml.SubElement(item, "source_x").text = str(posX)
                    xml.SubElement(item, "source_y").text = str(posY)

                xml.SubElement(item, "texture").text = os.path.basename(self.filepath)
                n+=1

        img_path = os.path.splitext(self.filepath)
        xml_path = img_path[0] + ".xml"

        XMLIndent(root)
        ExportXml(xml_path, root)

        return {'FINISHED'}
