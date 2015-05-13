The Bedazzler

To use:

Copy gui.py, bedazzle.py, and the 2 .ma files into your Maya scripts folder 
(on Mac: ~/Library/Preferences/Autodesk/maya/2015-x64/scripts)

then from Python Script Editor, run

import gui

To reopen gui, run

reload(gui)

--

Base Object can either be an entire mesh or a single face. If you have rotated your mesh, you must freeze transformations before running the script. 

Script works best on low poly meshes with planar faces. It also looks nicer when the faces are regularly sized. Works the best if you aren't planning on smoothing the mesh.

Parameters:

-Size: controls size of gems

-Spacing: controls amount of space between gems

-Overlap tolerance: Ranges from 0 to 1. 0 indicates no overlapping of gems. 1 means that gems can overlap by 50%. (Overlap won't occur except at the edges of faces)

-Smoothing: If 0, will use unsmoothed version of mesh to determine faces. Any values greater than 0 adjust the continuity. Maximum value of 1.0 smooths the faces as much as possible.

-Reducing mesh: Runs poly reduce with this value's percentage before finding the gem locations

(If smoothing and reducing, the mesh will be smoothed first, then reduced. Neither of these options will affect the original mesh.)

-Include shader: Applies a gem shader. If you run the script twice you will have duplicate copies of the shader in your file

-- 

Improvements to be made:

-Increase maximum of size and spacing parameters

-Allow to apply to multiple selected faces

-More organized grouping of gems for when script is run more than once

-Option to keep the proxy mesh that gems are placed based on (helpful for figuring out proper parameters and would make running script more than once faster)
