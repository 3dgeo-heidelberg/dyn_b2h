bl_info = {
    "name": "DynScene2HELIOS",
    "blender": (3, 4, 0),
    "version": (0, 1, 0),
    "author": "Hannah Weiser",
    "description": "Export dynamic scene to HELIOS",
    "category": "Scene"
}

import bpy
from dyn_b2h import operators, panel

modules = (operators, panel)

def register():
    for m in modules:
        m.register()


def unregister():
    for m in modules:
        m.unregister()


if __name__ == "__main__":
    register()