import bpy
import os
import sys
import math
from pathlib import Path
from swap_b2h import scene_writer as sw
import shutil


def flatten_compr(nested_list): 
    return [item for row in nested_list for item in row]


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
    # Print data paths of available animation/driver f-curves.
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
    print(layer_collection.name)
    objects = bpy.data.collections[layer_collection.name].all_objects
    # objects = layer_collection.children
    print([obj.name for obj in objects])
    for ob in objects:
        # objects.active = ob
        ob.select_set(True)
        i = 1
        if ob.type == 'MESH' and has_animation(ob):
            sp_name = ob.name
            outfile = str(Path(self.sceneparts_folder) / (sp_name + f'_{frame:03d}.obj'))
            filepaths_relative.append(Path(outfile).relative_to(self.helios_root))

            bpy.ops.export_scene.obj(filepath=outfile, use_selection=True, axis_up='Z', axis_forward='Y', use_materials=False)

        ob.select_set(False)

    return filepaths_relative


def export_obj_static(self, context, frame=0):
    # move to desired frame rate
    bpy.context.scene.frame_set(frame)

    # Deselect all objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    Path(self.sceneparts_folder).mkdir(parents=True, exist_ok=True)

    filepaths_relative = []
    # Iterate over all objects and export them
    objects = bpy.context.view_layer.objects
    print([obj.name for obj in objects])
    for ob in objects:
        objects.active = ob
        ob.select_set(True)

        i = 1
        if ob.type == 'MESH' and has_animation(ob) is False:
            print(ob)
            ob_name = ob.name
            if ob_name in filepaths_relative:
                ob_name = ob_name + f'{i:03d}'
                i += 1
            outfile = str(Path(self.sceneparts_folder) / (ob_name + '.obj'))

            filepaths_relative.append(Path(outfile).relative_to(self.helios_root))
            bpy.ops.export_scene.obj(filepath=outfile, use_selection=True, axis_up='Z', axis_forward='Y',
                                     use_materials=False)
        ob.select_set(False)

    return filepaths_relative


def reshape_list_by_prefix(swap_list):
    swap_list_flat = flatten_compr(swap_list)
    prefixes = set([ob_str.name.split("_")[0] for ob_str in swap_list_flat])
    swap_list_reshaped = []
    for prefix in prefixes:
        states = sorted([item for item in swap_list_flat if str(prefix) == item.name.split("_")[0]])
        swap_list_reshaped.append(states)
    
    return swap_list_reshaped


def write_scene(self, context, obj_paths_static, swap_list, frame, coll_name):
    """
    swap list looks like this
    a) one sublist for each epoch/frame
    [["cube_1.obj", "sphere_1.obj", "tree_1.obj"],
    ["cube_125.obj", "sphere_125.obj", "tree_125.obj"],
    ["cube_300.obj", "sphere_300.obj", "tree_300.obj"]}
    """
    sceneparts = ""

    # iterate through obj paths and create scenepart string
    for path in obj_paths_static:
        print(path)
        sp_string = sw.create_scenepart_obj(path)
        sceneparts += sp_string
    print(sceneparts)

    # transform swap list (by object) to swap list (by epoch)
    swap_list_by_epoch = reshape_list_by_prefix(swap_list)

    for swaps in swap_list_by_epoch:
        sp_string = sw.create_scenepart_swap(swaps)
        sceneparts += sp_string

    print(sceneparts)
    scene = sw.build_scene(scene_id=self.scene_id, name=self.scene_name, sceneparts=[sceneparts])

    filedir = Path(self.scene_folder)
    if len(self.scene_fname) > 0:
        scene_fname = self.scene_fname
    else:
        scene_fname = coll_name
    filename = scene_fname

    filepath_scene = (filedir / filename).as_posix()
    # write scene to file
    with open(filepath_scene, "w") as f:
        f.write(scene)


class OT_BatchExport_SwapSceneHelios(bpy.types.Operator):
    """HELIOS - Export moving scene to HELIOS"""
    bl_idname = "helios.export_swap_scene"
    bl_label = "Export OBJ swap scene"
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
        swap_list = []
        for layer_coll in layer_collections:
            static_fpaths = export_obj_static(export, context)

            for i, frame in enumerate(frame_list):  # each frame is an epoch
                # export objects (to OBJ files)
                dynamic_fpaths = export_obj_dyn(export, context, frame, layer_coll)
                swap_list.append(dynamic_fpaths)
        
            write_scene(export, context, static_fpaths, swap_list, frame, layer_coll.name)
            
        return {'FINISHED'}

classes = (OT_BatchExport_SwapSceneHelios,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
