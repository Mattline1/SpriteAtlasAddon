import os
import bpy

def GetTempFolder():
    #render_path = bpy.context.scene.render.filepath
    return os.path.join(bpy.app.tempdir, "tmp")

def CreateTempFolder():
    tmp = GetTempFolder()

    print(tmp)

    try:
        os.mkdir(tmp)
    except OSError:
        print("unable to create folder, it may already exist")

    # check output folder
    if not( os.path.exists(tmp) and os.path.isdir(tmp) ):
        print("invalid output directory")
        return False

    return True

def ClearFolder(folder):
    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)

        try:
            # delete files
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)

            # delete folders recursively
            elif os.path.isdir(file_path):
                ClearFolder(file_path)

        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    os.rmdir(folder)

def ClearTempFolder():
    ClearFolder(GetTempFolder())