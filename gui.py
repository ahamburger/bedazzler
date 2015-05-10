# from bedazzle import *
import maya.cmds as cmds

"""
Inspiried by Zeno Pelgrims' water drop generator gui
http://www.creativecrash.com/maya/script/water-drop-generator-python
"""

#ADD note about freezing transformations

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

	# info button
	cmds.button("infoButton", l="INFO", w=75, al="center", c=infoButton)

	# reset button
	cmds.button("resetButton", l="Reset Values", w=75, al="center", c=windowUI)

	# size
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("size", l="Gem Size: ", v=.25, min=0.001, max=1.0, f=True,w=370,pre=3)		#make real max bigger

	# padding
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("padding", l="Spacing: ", v=0, min=0.0, max=1.0, f=True,w=370,pre=3)	#make real max bigger
	
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("overlap", l="Overlap Tolerance: ", v=0, min=0.0, max=1.0, f=True,w=370,pre=3)	#make real max bigger
	
	cmds.separator(h=10, st='in')
		
	#smoothe
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("smoothe", l="Smoothe mesh: ", v=0, min=0.0, max=1.0, f=True,w=370,pre=3)

	# reduce mesh
	cmds.rowColumnLayout(w=380)
	cmds.intSliderGrp("meshReduce", l="% to reduce mesh: ", v=0, min=0, max=100, f=True,w=370)
	
	#shade
	cmds.checkBox("shaderCheckBox", l='Apply a simple shader', value=False)

	
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