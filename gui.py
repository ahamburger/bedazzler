from bedazzle import *
import maya.cmds as cmds

"""Mostly copied from Zeno Pelgrims' water drop generator gui
(ADD link)

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

	# generate button
	cmds.button("generateButton", l="~*~BEDAZZLE~*~", w=370, h = 40, al="center", bgc=[0.4,0.15,0.15], c=bedazzleButton)

	# reduce mesh
	cmds.rowColumnLayout(w=380)
	cmds.intSliderGrp("meshReduce", l="% to reduce mesh: ", v=0, min=0, max=100, f=True,w=370)
	
	# size
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("size", l="Gem Size: ", v=.25, min=0.01, max=1.0, f=True,w=370)		#make real max bigger

	# padding
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("padding", l="Spacing: ", v=0, min=0, max=1.0, f=True,w=370)	#make real max bigger
	
	#shade
	cmds.checkBox("shaderCheckBox", l='Apply a simple shader', value=False)

	# reset button
	cmds.button("resetButton", l="Reset to default values", w=370, al="center", c=windowUI)

	# text
	cmds.text(l='\nINFO\n', w=370, ww=True)
	cmds.text(l='The algorithm works best on objects with planar quads that are not too small in any one dimension.\n', w=370, al = 'left', ww=True)
	cmds.text(l='If your mesh has a lot of fine geometry, it is recommended that you use a poly-reduced mesh using the slider above. This will not modify your original geometry.', w=370,  al = 'left', ww=True)


	cmds.showWindow("windowUI")

def selectBaseObjectButton(*args):
	selectedObject = cmds.ls(sl=True, tr=True)
	pickBaseObject(selectedObject)

def bedazzleButton(*args):
	reduceMesh = cmds.intSliderGrp("meshReduce", query=True, v=True)
	size = cmds.floatSliderGrp("size", query=True, v=True)
	padding = cmds.floatSliderGrp("padding", query=True, v=True)
	shade = cmds. checkBox("shaderCheckBox", query=True, v=True)

	success = run(reduceMesh, size, padding, shade)
	if not success:
		

windowUI()