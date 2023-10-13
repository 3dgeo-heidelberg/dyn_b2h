import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ExportProps(bpy.types.PropertyGroup, ExportHelper):
    
    helios_root: bpy.props.StringProperty(name="Path to HELIOS++ root_folder", default="helios", subtype="DIR_PATH")
    sceneparts_folder: bpy.props.StringProperty(name="Name of sceneparts folder", default="")
    frame_step: bpy.props.IntProperty(name="Frame step", default=20)
    export_sceneparts: bpy.props.BoolProperty(name="Export scene parts?", default=True)
    scene_id: bpy.props.StringProperty(name="ID of the scene", default="scene")
    scene_name: bpy.props.StringProperty(name="Name of the scene", default="Scene")

class SCENE_PT_helios(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_idname = 'SCENE_PT_helios'
    bl_label = 'HELIOS'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        props = bpy.context.scene.ExportProps
        layout = self.layout
        
        # Create three rows for the input
        row = layout.row()
        row.label(text="HELIOS++ root folder")
        row.prop(props, "helios_root", text="")
        
        row = layout.row()
        row.label(text="Sceneparts folder")
        row.prop(props, "sceneparts_folder", text="")
        
        row = layout.row()
        row.label(text="Scene XML")
        row.prop(props, "filepath", text="")
        
        row = layout.row()
        row.label(text="Frame step")
        row.prop(props, "frame_step", text="")
        
        row = layout.row()
        row.prop(props, "export_sceneparts")
        
        split = layout.split()
        col = split.column()
        col.label(text="Scene ID")
        col.prop(props, "scene_id", text="")
        
        col = split.column(align=True)
        col.label(text="Scene name")
        col.prop(props, "scene_name", text="")

        row = layout.row()
        row.operator("helios.export", text="Export")

def export_button(self, context):
    self.layout.operator(
        OT_BatchExport_DynHelios.bl_idname,
        text="Batch Export OBJ dynamic",
        icon='PLUGIN')


 # Registration
def register():
    bpy.utils.register_class(SCENE_PT_helios)
    bpy.utils.register_class(ExportProps)
    # register ExportProps
    bpy.types.Scene.ExportProps = bpy.props.PointerProperty(type=ExportProps)


def unregister():
    bpy.utils.unregister_class(ExportProps)
    bpy.utils.unregister_class(SCENE_PT_helios)
    # $ delete ExportProps on unregister
    del(bpy.types.Scene.ExportProps)


if __name__ == "__main__":
    register()
