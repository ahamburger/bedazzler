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

	# reset button
	cmds.button("resetButton", l="Reset to default values", w=370, al="center", c=windowUI)

	# text
	cmds.text(l='', w=370, h=10, ww=True)
	cmds.text(l='Please bear in mind that the default size values XXXX', w=370, h=30, ww=True)
	cmds.text(l='The algorithm works best on objects with XXXX', w=370, h=30, ww=True)

	cmds.showWindow("windowUI")

def selectBaseObjectButton(*args):
	# variables
	selectedObject = cmds.ls(sl=True, tr=True)

	# call selectBaseObject function CHANGE THIS
	selectBaseObject(selectedObject)

def bedazzleButton(*args):
	# variables
	# dropDensity = cmds.intSliderGrp("dropDensity", query=True, v=True)
	# minDropSize = cmds.floatSliderGrp("minDropSize", query=True, v=True)
	# maxDropSize = cmds.floatSliderGrp("maxDropSize", query=True, v=True)
	# randomness = cmds.intSliderGrp("randomness", query=True, v=True)
	# optRandCheckBox = cmds.checkBox("optCheckBox", query=True, v=True)
	# smoothCheckBox = cmds.checkBox('smoothCheckBox', query=True, v=True)
	# shaderCheckBox = cmds.checkBox("shaderCheckBox", query=True, v=True)

	# call function
	run()
	# shade(shaderCheckBox)


windowUI()