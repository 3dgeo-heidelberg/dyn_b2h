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


def has_active_physics(obj):
    if obj.rigid_body:
        if obj.rigid_body.enabled is True and obj.rigid_body.type == 'ACTIVE':
            return True
        else:
            return False
    else:
        return False


def curve_to_mesh(self, context, frame):
    # move to desired frame rate
    bpy.context.scene.frame_set(frame)
    last_frame = bpy.context.scene.frame_end

    # Deselect all objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False) 
    
    converted = []
    # Iterate over all objects and export them
    objects = bpy.context.view_layer.objects

    for ob in objects:
        if ob.type == 'CURVE':
            objects.active = ob
            ob.select_set(True)
            bpy.ops.object.convert(target='MESH', keep_original=True)
            converted.append(ob.name)
            ob.select_set(False)
    
    # get last object (= new obj) and rename it
    new_obj = bpy.context.view_layer.objects[-1]
    new_name = new_obj.name.split('.')[0] + f'_{frame:03d}'
    new_obj.name = new_name
    new_obj.data.name = new_name
    converted.append(new_name)
    
    return converted


def export_obj_dyn(self, context, frame):
    # move to desired frame rate
    bpy.context.scene.frame_set(frame)
    last_frame = bpy.context.scene.frame_end
    
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
        i = 1
        if ob.type == 'MESH' and (has_animation(ob) or has_active_physics(ob)):
            ob_name = ob.name
            print(ob_name)
            if ob_name in filepaths_relative:
                ob_name = ob_name + f'{i:03d}'
                i += 1
            outfile = str(sceneparts_path / (ob_name + f'_{frame:03d}.obj'))
            
            filepaths_relative.append(Path(outfile).relative_to(self.helios_root))
            if has_active_physics(ob):
                area = [a for a in bpy.context.screen.areas if a.type=="VIEW_3D"][0]
                with bpy.context.temp_override(area=area):
                    # bake rigid body simulation to keyframes so object locations are properly exported
                    bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=last_frame)
        
            # condition is uncommented, because we expect that people usually want to export sceneparts
            # if self.export_sceneparts is True:
            bpy.ops.export_scene.obj(filepath=outfile, use_selection=True, axis_up='Z', axis_forward='Y', use_materials=self.write_materials)
            
        ob.select_set(False)
    
    return filepaths_relative


def export_obj_static(self, context, exclude_objects=[], frame=0):
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

        i = 1
        if ob.type == 'MESH' and has_animation(ob) is False and ob.name not in exclude_objects:
            ob_name = ob.name
            ob_basename, ob_frame = ob_name.split('_')
            if ob_name in filepaths_relative:
                ob_name = ob_name + f'{i:03d}'
                i += 1
            if not int(ob_frame) == frame:
                ob.select_set(False)
                continue
            outfile = str(sceneparts_path / (ob_name + '.obj'))

            filepaths_relative.append(Path(outfile).relative_to(self.helios_root))
            bpy.ops.export_scene.obj(filepath=outfile, use_selection=True, axis_up='Z', axis_forward='Y',
                                     use_materials=self.write_materials)
        ob.select_set(False)

    return filepaths_relative


def write_static_scene(self, context, obj_paths_static, obj_paths_dynamic, frame):
    
    sceneparts = ""
    
    # iterate through static obj paths and create scenepart string
    for path in obj_paths_static + obj_paths_dynamic:
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


class OT_BatchExport_MultiEpochHelios(bpy.types.Operator):
    """HELIOS - Export moving scene to HELIOS"""
    bl_idname = "helios.export_multi_epoch"
    bl_label = "Export OBJ multi epoch"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        export = scene.ExportProps_me
        # fix sceneparts path if necessary
        sceneparts_dir = Path(export.helios_root) / "data/sceneparts"
        if Path(export.sceneparts_folder).is_relative_to(sceneparts_dir):
            export.sceneparts_folder = (Path(export.sceneparts_folder).relative_to(sceneparts_dir)).as_posix()

        # export static sceneparts and get their paths
        static_fpaths = export_obj_static(export, context)

        # get frames to export
        try:
            frame_list = [int(frame) for frame in export.frame_list.split(",")]
        except:
            frame_list = []
        if len(frame_list) == 0:
            frame_list = list(range(scene.frame_start, scene.frame_end + export.frame_step, export.frame_step))

        # iterate over frrames and export objects
        for frame in frame_list:
            # convert animated curves to mesh
            converted_objects = curve_to_mesh(export, context, frame)
            # export converted meshes (for that frame)
            converted_static_fpaths = export_obj_static(export, context, exclude_objects=static_fpaths, frame=frame)
            # export dynamic meshes (at the state of the current frame)
            dynamic_fpaths = export_obj_dyn(export, context, frame)
            dynamic_fpaths += converted_static_fpaths
            
            # write the static scene XMLs (as seen at the current frame)
            write_static_scene(export, context, static_fpaths, dynamic_fpaths, frame)
            
        return {'FINISHED'}

classes = (OT_BatchExport_MultiEpochHelios,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
