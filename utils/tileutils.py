import bpy
import os
import math

def CeilToMultiple(number, multiple):
    return multiple * math.ceil(float(number) / float(multiple))

def AutoImageSize(width, height, count):
    sqr_count =  math.ceil(math.sqrt(count))
    lin_len_x = width * sqr_count
    lin_len_y = height * sqr_count
    return (lin_len_x, lin_len_y)

def PasteImage(target, source, posx, posy, image_height):
    target_pixels = list(target.pixels)
    source_pixels = list(source.pixels)
    width  = source.size[0]
    height = source.size[1]

    posy = image_height - posy - height

    for Y in range(0, height):
        for X in range(0, width):
            sp = int(X + (Y * width))
            tp = int((X + posx)  + ((Y + posy) * target.size[0]))

            sp *= source.channels
            tp *= target.channels

            for C in range(0, min(source.channels, target.channels)):
                target_pixels[tp + C] = source_pixels[sp + C]

    target.pixels[:] = target_pixels
    target.update()

def GetTilePos(width, height, image_width, image_height, i):
    posX = (i * width) % image_width
    posY = int((i * width) / image_height) * height
    return (posX, posY)

def TilePathsIntoImage(spritesheet_name_string, image_path_list, width, height):
    # create spritesheet image
    spritesheet = None

    # check if sprite sheet exists
    if spritesheet_name_string in bpy.data.images:
        spritesheet = bpy.data.images[spritesheet_name_string]

        if spritesheet.resolution[0] != width or spritesheet.resolution[1] != width:
            bpy.data.images.remove(spritesheet)
            spritesheet = bpy.data.images.new(spritesheet_name_string, width, height, alpha=True)

    else:
        # else create it
        spritesheet = bpy.data.images.new(spritesheet_name_string, width, height, alpha=True)

    # load sprites and append into sheet
    for i in range(len(image_path_list)):

        # locals
        path = image_path_list[i]
        img = None

        # try to load image into blender
        try:
            img = bpy.data.images.load(path)
        except:
            raise NameError("Cannot load image %s" % path)

        posX, posY = GetTilePos(img.size[0], img.size[1], spritesheet.size[0], spritesheet.size[1], i)
        PasteImage(spritesheet, img, posX, posY, width)

        bpy.data.images.remove(img)

    return spritesheet