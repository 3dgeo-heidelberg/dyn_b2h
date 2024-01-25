import bpy
import os
import sys
import numpy as np
import math
from mathutils import Quaternion, Matrix, Euler, Vector
from pathlib import Path
from bpy_extras.io_utils import ImportHelper, ExportHelper
from multi_epoch_b2h import scene_writer as sw
import shutil


def add_material(outfile, matfile, matname):
    with open(outfile, 'r+') as f:
        data = f.readlines()
        data.insert(2, f'mtllib {matfile}\n')
        data.insert(3, f'usemtl {matname}\n')
        f.seek(0)
        f.writelines(data)

def has_animation(obj):
    # Collect places where animation/driver data possibly present.
    keyable_list = [getattr(obj.data, 'shape_keys', None)]
    if obj.particle_systems:
        for ps in obj.particle_systems:
            keyable_list.append(ps.settings)
    keyable_list.append(obj)
    keyable_list.append(obj.data)

    # may also be present in texture coords object of a displacement modifier
    modifiers = []
    for modifier in obj.modifiers:
        modifiers.append(modifier)

    animation = False
    for keyable in keyable_list:
        if not keyable or not keyable.animation_data:
            continue
        else:
            action = keyable.animation_data.action
            driver = keyable.animation_data.drivers
            if action:
                animation = True
            if driver:
                animation = True

    for modifier in modifiers:
        if modifier.type == "DISPLACE":
            if modifier.texture_coords_object.animation_data:
                animation = True
        elif modifier.type == "ARMATURE":
            if modifier.object.animation_data:
                animation = True
    return animation


def export_obj_dyn(self, context, frame, layer_collection):

    # move to desired frame rate
    bpy.context.scene.frame_set(frame)

    # Deselect all objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    Path(self.sceneparts_folder).mkdir(parents=True, exist_ok=True)
    filepaths_relative = []
    # Iterate over all objects and export them
    # print(layer_collection.name)
    objects = bpy.data.collections[layer_collection.name].all_objects
    # print([obj.name for obj in objects])
    for ob in objects:
        ob.select_set(True)
        if ob.type == 'MESH' and has_animation(ob):
            if len(self.sceneparts_fname) > 0:
                sp_name = self.sceneparts_fname
            else:
                sp_name = layer_collection.name
            print(sp_name)
            outfile = str(Path(self.sceneparts_folder) / (sp_name + f'_{frame:03d}.obj'))
            filepaths_relative.append(Path(outfile).relative_to(self.helios_root))

            bpy.ops.export_scene.obj(filepath=outfile, use_selection=True, axis_up='Z', axis_forward='Y', use_materials=False)

        ob.select_set(False)

    return filepaths_relative


def write_scene(self, context, obj_paths_static, obj_paths_dynamic,frame, coll_name):

    sceneparts = ""

    # iterate through obj paths and create scenepart string
    for path in obj_paths_static + obj_paths_dynamic:
        sp_string = sw.create_scenepart_obj(path)
        sceneparts += sp_string

    scene = sw.build_scene(scene_id=self.scene_id, name=self.scene_name, sceneparts=[sceneparts])

    filedir = Path(self.scene_folder)
    if len(self.scene_fname) > 0:
        scene_fname = self.scene_fname
    else:
        scene_fname = coll_name
    filename = scene_fname + f"_{frame:03d}.xml"

    filepath_static = (filedir / filename).as_posix()
    # write scene to file
    with open(filepath_static, "w") as f:
        f.write(scene)


class OT_BatchExport_MultiEpochHelios(bpy.types.Operator):
    """HELIOS - Export moving scene to HELIOS"""
    bl_idname = "helios.export_multi_epoch"
    bl_label = "Export OBJ multi epoch"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        export = scene.ExportProps_me

        try:
            frame_list = [int(frame) for frame in export.frame_list.split(",")]
        except:
            frame_list = []
        if len(frame_list) == 0:
            frame_list = list(range(scene.frame_start, scene.frame_end + export.frame_step, export.frame_step))

        # get all collections
        layer_collections = bpy.context.view_layer.layer_collection.children
        layer_collections = [coll for coll in layer_collections if coll.is_visible]
        print(layer_collections)
        for layer_coll in layer_collections:
            for frame in frame_list:
                # export objects (to OBJ files)
                dynamic_fpaths = export_obj_dyn(export, context, frame, layer_coll)
                if export.filepath != "":
                    static_path = Path(export.filepath).relative_to(export.helios_root)
                    static_fpaths = [static_path]
                else:
                    static_fpaths = []

                if len(dynamic_fpaths) > 0:
                    # write the scene XMLs
                    write_scene(export, context, static_fpaths, dynamic_fpaths, frame, layer_coll.name)
            
        return {'FINISHED'}

classes = (OT_BatchExport_MultiEpochHelios,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
