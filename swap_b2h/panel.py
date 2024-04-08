import bpy
from bpy_extras.io_utils import ExportHelper


class ExportProps_me(bpy.types.PropertyGroup, ExportHelper):
    
    helios_root: bpy.props.StringProperty(name="Path to HELIOS++ root_folder", default="helios", subtype="DIR_PATH")
    sceneparts_folder: bpy.props.StringProperty(name="Path of scene parts folder", default="", subtype="DIR_PATH")
    scene_folder: bpy.props.StringProperty(name="Path to the scene folder to create and write scenes into", default="", subtype="DIR_PATH")
    scene_fname: bpy.props.StringProperty(name="Name of scene file (suffix for frame will be appended)", default="")
    frame_step: bpy.props.IntProperty(name="Frame step", default=20)
    frame_list: bpy.props.StringProperty(name="List of frames", default="")
    only_active: bpy.props.BoolProperty(name="Export only active objects?", default=True)
    scene_id: bpy.props.StringProperty(name="ID of the scene", default="scene")
    scene_name: bpy.props.StringProperty(name="Name of the scene", default="Scene")

class SCENE_PT_helios_me(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_idname = 'SCENE_PT_helios_swap_scene'
    bl_label = 'HELIOS SWAP SCENE'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        props = bpy.context.scene.ExportProps_me
        layout = self.layout
        
        # Create three rows for the input
        row = layout.row()
        row.label(text="HELIOS++ root folder")
        row.prop(props, "helios_root", text="")
        
        row = layout.row()
        row.label(text="Scene parts folder")
        row.prop(props, "sceneparts_folder", text="")
        
        row = layout.row()
        row.label(text="Scene XML folder")
        row.prop(props, "scene_folder", text="")

        row = layout.row()
        row.label(text="Scene filename")
        row.prop(props, "scene_fname", text="")

        split = layout.split()
        col = split.column()
        col.label(text="Frame step")
        col.prop(props, "frame_step", text="")

        col = split.column(align=True)
        col.label(text="List of frames (comma separated)")
        col.prop(props, "frame_list", text="")

        row = layout.row()
        row.prop(props, "only_active")
        
        split = layout.split()
        col = split.column()
        col.label(text="Scene ID")
        col.prop(props, "scene_id", text="")
        
        col = split.column(align=True)
        col.label(text="Scene name")
        col.prop(props, "scene_name", text="")

        row = layout.row()
        row.operator("helios.export_swap_scene", text="Export")

def export_button(self, context):
    self.layout.operator(
        OT_BatchExport_SwapSceneHelios.bl_idname,
        text="Batch Export OBJ dynamic",
        icon='PLUGIN')


 # Registration
def register():
    bpy.utils.register_class(SCENE_PT_helios_me)
    bpy.utils.register_class(ExportProps_me)
    # register ExportProps
    bpy.types.Scene.ExportProps_me = bpy.props.PointerProperty(type=ExportProps_me)


def unregister():
    bpy.utils.unregister_class(ExportProps_me)
    bpy.utils.unregister_class(SCENE_PT_helios_me)
    # $ delete ExportProps on unregister
    del bpy.types.Scene.ExportProps_me


if __name__ == "__main__":
    register()
