bl_info = {
    "name": "Scenes2HELIOS",
    "blender": (3, 4, 0),
    "version": (0, 1, 0),
    "author": "Hannah Weiser",
    "description": "Export dynamic scene to HELIOS by exporting objects at different frames",
    "category": "Scene"
}

import bpy
from multi_epoch_b2h import operators, panel

modules = (operators, panel)

def register():
    for m in modules:
        m.register()


def unregister():
    for m in modules:
        m.unregister()


if __name__ == "__main__":
    register()