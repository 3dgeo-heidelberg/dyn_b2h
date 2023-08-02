
import bpy
import os
import sys
import numpy as np
import math
from mathutils import Quaternion, Matrix, Euler, Vector
from pathlib import Path
from bpy_extras.io_utils import ImportHelper, ExportHelper
from movingtree2helios import scene_writer as sw


def export_obj(self, context):
    # make sure, we are at frame 0
    bpy.context.scene.frame_set(0)
    
    # Deselect all objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False) 

    sceneparts_path = Path(self.helios_root) / (f"data/sceneparts/{self.sceneparts_folder}")
    sceneparts_path.mkdir(parents=True, exist_ok=True)
    
    filepaths_relative = []
    # Iterate over all objects and export them
    objects = bpy.context.view_layer.objects
    for ob in objects:
        objects.active = ob
        ob.select_set(True)

        if ob.type == 'MESH':
            outfile = str(sceneparts_path / (ob.name + '.obj'))
            
            filepaths_relative.append(Path(outfile).relative_to(self.helios_root))
            if self.export_sceneparts is True:
                bpy.ops.export_scene.obj(filepath=outfile, use_selection=True, axis_up='Z', axis_forward='Y', use_materials=False)

        ob.select_set(False)
    
    return filepaths_relative
    

def write_dyn_scene(self, context, obj_paths_relative):
    obj_paths_dynamic = []
    obj_paths_static = []
    sceneparts = ""

    
    objects = bpy.context.view_layer.objects
    objects = [ob for ob in objects if ob.type == 'MESH']
    
    fps = bpy.context.scene.render.fps
    
    for i, ob in enumerate(objects):
        frames = []
        rotations = []
        locations = []
        try:
            for f in ob.animation_data.action.fcurves:
                for k in f.keyframe_points:
                    fr = k.co[0]
                    bpy.context.scene.frame_set(int(fr))
                    frames.append(int(fr))
                    rotations.append(ob.rotation_euler.copy().freeze())
                    locations.append(ob.location.copy().freeze())
                break
        except AttributeError:
            # ignore attribute error - happens on objects without animation data, e.g., the tree stem
            pass
        # check if moving object (i.e., rotations are different between keyframes)
        if len(set(rotations)) or len(set(locations)) > 1:
            sceneparts += "\n        <!--Dynamic scenepart-->"
            dynm_string = ""
            leaf_id = str(obj_paths_relative[i]).split("\\")[-1].replace(".obj", "")
            path = str(obj_paths_relative[i])
            # make sure we are at frame 0
            prev_frame = 0
            bpy.context.scene.frame_set(0)
            initial_loc = ob.location.copy().freeze()
            initial_rot = ob.rotation_euler.copy().freeze().to_quaternion()
            j = 0
            prev_loc = initial_loc
            prev_rot = initial_rot
            for frame, rot, loc in zip(frames, rotations, locations):
                # determines number of loops
                frame_diff = frame - prev_frame
                if frame_diff == 0:
                    j += 1
                    continue
                
                rot_centre = loc
                
                # get rotation between actual and previous
                # current rotation to Quaternion
                q_rot = rot.to_quaternion()

                # subtract rotations -> multiply by inverse
                new_rot = q_rot @ prev_rot.inverted()
                
                # new rotation to axis angle
                axis, angle = new_rot.to_axis_angle()
                axis = axis[:]
                angle = np.rad2deg(angle)
                
                new_t = loc - prev_loc
                
                # determine whether to continue with next dmotion or with first one (i.e., restart loop)
                if j+1 == len(frames):
                    # only write the next motion if the animation shall be displayed in a loop
                    if self.loop_animations:
                        next_id = 1
                        prev_frame = 0
                        new_t = initial_loc - loc
                        new_rot = q_rot @ initial_rot.inverted()
                    else:    
                        break    
                else:
                    next_id = j+1
                    if next_id+1 == len(frames) and self.loop_animations is False:
                        next_id = False
                    prev_frame = frame
                    prev_rot = rot.to_quaternion()
                    prev_loc = loc
                if next_id:
                    next = f"{leaf_id}_{next_id}"
                else:
                    next = False
                # add to dynamic motion string
                dynm_string += sw.add_motion_rot_tran(id = f"{leaf_id}_{j}", axis=axis, angle=angle, x=new_t[0], y=new_t[1], z=new_t[2], rotation_center=rot_centre, nloops=1, next=next)
                j+= 1
            sp_string = sw.create_scenepart_obj(path, motionfilter=dynm_string, kdt_dyn_step=10/24)
            sceneparts += sp_string     
                    
        else:
            # add to list with static objects
            obj_paths_static.append(obj_paths_relative[i])
    
    # iterate through static obj paths and create scenepart string
    sceneparts += "\n        <!--Static sceneparts-->"
    for path in obj_paths_static:
        sp_string = sw.create_scenepart_obj(path)
        sceneparts += sp_string
    
    dyn_t_step = frame_diff / fps
    scene = sw.build_scene(scene_id=self.scene_id, name=self.scene_name, sceneparts=[sceneparts], dyn_time_step=dyn_t_step)
    
    # write scene to file
    with open(self.filepath, "w") as f:
        f.write(scene)


def write_static_scene(self, context, obj_paths_relative):
    
    sceneparts = ""
    
    # iterate through static obj paths and create scenepart string
    for path in obj_paths_relative:
        sp_string = sw.create_scenepart_obj(path)
        sceneparts += sp_string
    
    scene = sw.build_scene(scene_id=self.scene_id, name=self.scene_name, sceneparts=[sceneparts])
    
    filedir = Path(self.filepath).parent
    filename_parts = Path(self.filepath).stem.split("_")
    if len(filename_parts) > 1:
        filename = "_".join(filename_parts[:-1]) + "_static.xml"
    else:
        filename = filename_parts[0] + "_static.xml"
    
    filepath_static = (filedir / filename).as_posix()
    # write scene to file
    with open(filepath_static, "w") as f:
        f.write(scene)


# multiply 3d coord list by matrix
def np_matmul_coords(coords, matrix, space=None):
    M = (space @ matrix @ space.inverted()
         if space else matrix).transposed()
    ones = np.ones((coords.shape[0], 1))
    coords4d = np.hstack((coords, ones))
    
    return np.dot(coords4d, M)[:,:-1]


class OT_BatchExport_DynHelios(bpy.types.Operator):
    """HELIOS - Export moving scene to HELIOS"""
    bl_idname = "helios.export"
    bl_label = "Export OBJ dynamic"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        export = scene.ExportProps
        
        # export objects (to OBJ files) 
        relative_fpaths = export_obj(export, context)
        
        # write the scene XML (incl. motions)
        write_dyn_scene(export, context, relative_fpaths)
        
        # write the static scene XML (if filepath is provided)
        if export.export_static is True:
            write_static_scene(export, context, relative_fpaths)
        
        return {'FINISHED'}

classes = (OT_BatchExport_DynHelios,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
