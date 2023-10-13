import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ExportProps_dyn(bpy.types.PropertyGroup, ExportHelper):
    
    helios_root: bpy.props.StringProperty(name="Path to HELIOS++ root_folder", default="helios", subtype="DIR_PATH")
    sceneparts_folder: bpy.props.StringProperty(name="Name of sceneparts folder", default="")
    loop_animations: bpy.props.BoolProperty(name="Loop animations?", default=False)
    export_static: bpy.props.BoolProperty(name="Also export static scene?", default=True)
    export_sceneparts: bpy.props.BoolProperty(name="Export scene parts?", default=True)
    scene_id: bpy.props.StringProperty(name="ID of the scene", default="dyn_scene")
    scene_name: bpy.props.StringProperty(name="Name of the scene", default="Dynamic scene")

class SCENE_PT_helios_dyn(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_idname = 'SCENE_PT_helios_dyn'
    bl_label = 'HELIOS DYNAMIC'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        props = bpy.context.scene.ExportProps_dyn
        layout = self.layout
        
        # Create three rows for the input
        row = layout.row()
        row.label(text="HELIOS++ root folder")
        row.prop(props, "helios_root", text="")
        
        row = layout.row()
        row.label(text="Sceneparts folder")
        row.prop(props, "sceneparts_folder", text="")
        
        row = layout.row()
        row.label(text="Dynamic scene XML")
        row.prop(props, "filepath", text="")
        
        row = layout.row()
        row.prop(props, "loop_animations")
        
        row = layout.row()
        row.prop(props, "export_static")
        
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
        row.operator("helios.export_dyn", text="Export")

def export_button(self, context):
    self.layout.operator(
        OT_BatchExport_DynHelios.bl_idname,
        text="Batch Export OBJ dynamic",
        icon='PLUGIN')


 # Registration
def register():
    bpy.utils.register_class(SCENE_PT_helios_dyn)
    bpy.utils.register_class(ExportProps_dyn)
    # register ExportProps
    bpy.types.Scene.ExportProps_dyn = bpy.props.PointerProperty(type=ExportProps_dyn)


def unregister():
    bpy.utils.unregister_class(ExportProps_dyn)
    bpy.utils.unregister_class(SCENE_PT_helios_dyn)
    # $ delete ExportProps on unregister
    del(bpy.types.Scene.ExportProps_dyn)


if __name__ == "__main__":
    register()
