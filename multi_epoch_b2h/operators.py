
import bpy
import os
import sys
import numpy as np
import math
from mathutils import Quaternion, Matrix, Euler, Vector
from pathlib import Path
from bpy_extras.io_utils import ImportHelper, ExportHelper
from dyn_b2h import scene_writer as sw
import shutil


def add_material(outfile, matfile, matname):
    with open(outfile, 'r+') as f:
        data = f.readlines()
        data.insert(2, f'mtllib {matfile}\n')
        data.insert(3, f'usemtl {matname}\n')
        f.seek(0)
        f.writelines(data)


def export_obj(self, context, frame):
    # move to desired frame rate
    bpy.context.scene.frame_set(frame)
    
    # Deselect all objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False) 

    sceneparts_path = Path(self.helios_root) / (f'data/sceneparts/{self.sceneparts_folder}')
    sceneparts_path.mkdir(parents=True, exist_ok=True)
    
    filepaths_relative = []
    # Iterate over all objects and export them
    objects = bpy.context.view_layer.objects
    for ob in objects:
        objects.active = ob
        ob.select_set(True)

        if ob.type == 'MESH':
            outfile = str(sceneparts_path / (ob.name + f'_{frame:03d}.obj'))
            
            filepaths_relative.append(Path(outfile).relative_to(self.helios_root))
            if self.export_sceneparts is True:
                bpy.ops.export_scene.obj(filepath=outfile, use_selection=True, axis_up='Z', axis_forward='Y', use_materials=False)
                # add material library
                mtllib = 'tree.mtl'
                if 'tree' in ob.name:
                    mtl = 'wood'
                elif 'leaves' in ob.name:
                    mtl = 'leaves'
                else:
                    break
                # add material reference to written OBJ
                add_material(outfile, mtllib, mtl)
                    

        ob.select_set(False)
    
    return filepaths_relative


def write_static_scene(self, context, obj_paths_relative, frame):
    
    sceneparts = ""
    
    # iterate through static obj paths and create scenepart string
    for path in obj_paths_relative:
        sp_string = sw.create_scenepart_obj(path)
        sceneparts += sp_string
    
    scene = sw.build_scene(scene_id=self.scene_id, name=self.scene_name, sceneparts=[sceneparts])
    
    filedir = Path(self.filepath).parent
    filename = Path(self.filepath).stem
    filename = filename + f"_{frame:03d}.xml"
    
    filepath_static = (filedir / filename).as_posix()
    # write scene to file
    with open(filepath_static, "w") as f:
        f.write(scene)


class OT_BatchExport_DynHelios(bpy.types.Operator):
    """HELIOS - Export moving scene to HELIOS"""
    bl_idname = "helios.export"
    bl_label = "Export OBJ dynamic"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        export = scene.ExportProps
        
        for frame in range(scene.frame_start, scene.frame_end + export.frame_step, export.frame_step):
            # export objects (to OBJ files) 
            relative_fpaths = export_obj(export, context, frame)
            
            # write the static scene XMLs
            write_static_scene(export, context, relative_fpaths, frame)
            
        return {'FINISHED'}

classes = (OT_BatchExport_DynHelios,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
