bl_info = {
    "name": "Scenes2HELIOS",
    "blender": (3, 4, 0),
    "version": (0, 1, 0),
    "author": "Hannah Weiser",
    "description": "Export dynamic scene to HELIOS by exporting objects at different frames",
    "category": "Scene"
}

# When bpy is already in local, we know this is not the initial import...
if "bpy" in locals():
    # ...so we need to reload our submodule(s) using importlib
    import importlib
    if "multi_epoch_b2h.operators" in locals():
        importlib.reload(multi_epoch_b2h.operators)
    if "multi_epoch_b2h.panel" in locals():
        importlib.reload(multi_epoch_b2h.panel)

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