from bedazzle import *
import maya.cmds as cmds

"""
To use The Bedazzler:

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

	Size: controls size of gems

	Spacing: controls amount of space between gems

	Overlap tolerance: Ranges from 0 to 1. 0 indicates no overlapping of gems. 1 means that gems can overlap by 50%. (Overlap won't occur except at the edges of faces)

	Smoothing: If 0, will use unsmoothed version of mesh to determine faces. Any values greater than 0 adjust the continuity. Maximum value of 1.0 smooths the faces as much as possible.

	Reducing mesh: Runs poly reduce with this value's percentage before finding the gem locations

	(If smoothing and reducing, the mesh will be smoothed first, then reduced. Neither of these options will affect the original mesh.)

	Include shader: Applies a gem shader. If you run the script twice you will have duplicate copies of the shader in your file


GUI inspired by Zeno Pelgrims' water drop generator gui
http://www.creativecrash.com/maya/script/water-drop-generator-python
"""

def windowUI(*args):

	if cmds.window("windowUI", exists=True):
		cmds.deleteUI("windowUI")
	cmds.window("windowUI", title="Bedazzler", resizeToFitChildren = True, sizeable = False)

	# base object layout
	cmds.frameLayout(label = "General", collapsable=False, mw=5, mh=5)
	cmds.rowColumnLayout(nc=3, cal=[(1,"right")], cw=[(1,80),(2,200),(3,95)])
	

	cmds.text(l="Base Object: ")
	cmds.textField("baseObject")
	cmds.button("baseObjectButton", l="Select", c=selectBaseObjectButton)
	
	cmds.setParent("..")
	cmds.separator(h=10, st='in')

	# # info button
	# cmds.button("infoButton", l="INFO", w=75, al="center", c=infoButton)

	# reset button
	cmds.button("resetButton", l="Reset Values", w=75, al="center", c=windowUI)

	# size
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("size", l="Gem Size: ", v=.25, min=0.001, max=1.0, f=True,w=370,pre=3)

	# padding
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("padding", l="Spacing: ", v=0, min=0.0, max=1.0, f=True,w=370,pre=3)
	
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("overlap", l="Overlap Tolerance: ", v=0, min=0.0, max=1.0, f=True,w=370,pre=3)
	
	cmds.separator(h=10, st='in')
		
	#smoothe
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("smoothe", l="Smooth mesh: ", v=0, min=0.0, max=1.0, f=True,w=370,pre=3)

	# reduce mesh
	cmds.rowColumnLayout(w=380)
	cmds.intSliderGrp("meshReduce", l="% to reduce mesh: ", v=0, min=0, max=100, f=True,w=370)
	
	#shade
	cmds.checkBox("shaderCheckBox", l='Include shader', value=False)

	
	# # text
	# cmds.text(l='\nINFO\n', w=370, ww=True)
	# cmds.text(l='The algorithm works best on objects with planar quads that are not too small in any one dimension.\n', w=370, al = 'left', ww=True)
	# cmds.text(l='If your mesh has a lot of fine geometry, it is recommended that you use a poly-reduced mesh using the slider above. This will not modify your original geometry.', w=370,  al = 'left', ww=True)
	cmds.separator(h=10, st='in')

	# bedazzle button
	cmds.button("bedazzleButton", l="~*~BEDAZZLE~*~", w=370, h = 40, al="center", bgc=[0.14,0.94,0.86], c=bedazzleButton)

	cmds.showWindow("windowUI")

def selectBaseObjectButton(*args):
	selectedObject = cmds.ls(sl=True, fl=True)
	pickBaseObject(selectedObject)
	global isObj
	isObj = False
	if 'transform' in cmds.ls(sl=True, fl=True, st=True):
		isObj = True

def infoButton(*args):
	cmds.promptDialog(
		title='Info',
		message='Info',
		button=['OK'],
		defaultButton='OK',
		dismissString='OK')

def bedazzleButton(*args):
	reduceMesh = cmds.intSliderGrp("meshReduce", query=True, v=True)
	size = cmds.floatSliderGrp("size", query=True, v=True)
	padding = cmds.floatSliderGrp("padding", query=True, v=True)
	shade = cmds.checkBox("shaderCheckBox", query=True, v=True)
	smoothe = cmds.floatSliderGrp("smoothe", query=True, v=True)
	overlap = cmds.floatSliderGrp("overlap", query=True, v=True)

	success = run(isObj, reduceMesh, size, padding, shade, smoothe, overlap)
		
windowUI()