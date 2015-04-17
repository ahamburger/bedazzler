import maya.cmds as cmds
import maya.OpenMaya as OM


def bedazzle():
	base = pickBaseObject()
	makeGem()
	placeGem()

#return first object in the scene (for now) except for gemstones
def pickBaseObject():
	objects = cmds.ls();
	if len(objects)==0:
		print("No objects in scene")
		return
	for o in objects:
		if not o.contains("gem"):
			return o


#make gem geometry (one for now)
def makeGem():
	cmds.polyCube(name="gem")
	cmds.polyMoveEdge( 'gem.e[1:2]', s=(.75, .75, .75) )
	cmds.polyMoveEdge( 'gem.e[6:7]', s=(.75, .75, .75) )		#not sure this line is necessary
	cmds.polyMoveEdge( 'gem.e[1:2]', t=(0, -.5, 0) )

#place gem on a 
def placeGem():


"""
GAME PLAN:
Get base object vertices
Convert to UV coordinates

(assume UVs are continuously connected, for now)
Find width and height of bounding box of UVs (min/max x/y values)
Get number of gems needed (ie how many rows and columns) by taking bounding box width / gem width and same for heights
Figure out upper left corner (or center?) of all these gems in terms of UV coordinates

Convex hull:
sort UV coordinates in order based on angle with an anchor point
Iterate over gem rows
	If center point(could also maybe check all 4 corners?) makes convex angle w closest 2 vertices (ie outside of them) 
		remove it from list

Convert UVs of gems to world space
Get normals at those world space points
Translate and rotate gems so they are at the world space point, facing up


Still need to address:
UVs being disconnected
How to select base object

"""
