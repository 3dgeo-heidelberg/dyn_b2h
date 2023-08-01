# dyn_b2h

Blender Add-on for exporting dynamic/animated scenes from Blender to HELIOS++

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

This Blender Add-on allows exporting an animated Blender scene to a HELIOS++ scene. It involves exporting the scene parts (OBJ files) and writing a scene file with sequences of rigid motions for the dynamic objects. As of now, it supports simple motions composed of translations and rotations.

<!-- GETTING STARTED -->
## Getting Started

The Blender add-on is contained in the folder `dyn_b2h`.

### Prerequisites

- [Blender](https://www.blender.org/) (version 3.4.0)
- [HELIOS++](https://github.com/3dgeo-heidelberg/helios)
- Clone or download this repository

### Installation

The [dyn_b2h](https://github.com/3dgeo-heidelberg/dyn_b2h/tree/main/dyn_b2h) add-on contains several modules. Prior to installing it, zip the folder *dyn_b2h*. In Blender, go to Edit -> Preferences... -> Add-ons. Here, click on "Install..." and navigate to the zip folder *dyn_b2h.zip* using the file browser. The installed add-on now appears in the menu. Activate the add-on by clicking on the checkmark. If you now go to the "Scene Properties" ![image](https://github.com/3dgeo-heidelberg/dyn_b2h/assets/41050948/8835af09-92c2-47f6-b518-307d95c17ac6)
tag in the "Properties" Window ![image](https://github.com/3dgeo-heidelberg/dyn_b2h/assets/41050948/4aa3d38f-3bc7-4166-9f60-8166aae3b2d3), you should see a new menu "HELIOS".

<!-- USAGE EXAMPLES -->
## Usage

Create any scene in Blender, which you want to run a simulation on. The scene can include animations, in which case a dynamic scene will be created. Before exporting a dynamic scene, make sure to bake it. Select the animated object, and then (in Object mode), select Object -> Animation -> Bake Action... Select the desired start frame, end frame and frame step and click OK. 


Now you are ready for exporting the scene. Go to the HELIOS menu in the "Scene Properties", which looks like this:

![image](https://github.com/3dgeo-heidelberg/dyn_b2h/assets/41050948/f5ddb05c-9db0-46e0-8b51-fb1171772145)

Select your HELIOS++ root folder and the name of your sceneparts subfolder. This name will automatically be appended to `<your-helios-root_dir>/data/sceneparts`. The add-on will export the meshes in your Blender scene to this folder in OBJ format. Furthermore, browse for the XML file to which the dynamic scene shall be written.

In the three checkboxes, you can decide
- whether to loop the animations or stop the rigid motions after the animations have completed.
- whether to also export a static version of the scene (i.e. without animations: dynamic objects will have the position and orientation that they have at frame 0).
- whether to export scene parts. This may be unchecked if you re-export your scene multiple times after changing the animation, but not the objects itself, so the files do not have to be written each time (which may take quite a while).

Lastly, define an ID and name for your scene, which will be written into the scene XML file.

When you are ready, hit "Export" and wait for the export to complete.

You can now use the generated scene XML to run a HELIOS++ simulation. Simply create a [survey XML](https://github.com/3dgeo-heidelberg/helios/wiki/Survey) file which performs a simulated laser scanning survey over the scene. Execute the survey with HELIOS++.

<!-- LICENSE -->
## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE.
See [LICENSE]((https://github.com/3dgeo-heidelberg/dyn_b2h/blob/main/LICENSE)).



<!-- CONTACT -->
## Contact

Hannah Weiser - h.weiser@uni-heidelberg.de

- Project Link: [https://github.com/3dgeo-heidelberg/dyn_b2h/](https://github.com/3dgeo-heidelberg/dyn_b2h/)
- 3DGeo Website: [www.uni-heidelberg.de/3dgeo](https://www.geog.uni-heidelberg.de/3dgeo/index.html)
