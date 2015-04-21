import maya.cmds as cmds
import maya.OpenMaya as OM
import math

def run():
	base = pickBaseObject()
	g = makeGem()
	placeGem(base, g)

#return first object in the scene (for now) except for gemstones
def pickBaseObject():
	objects = cmds.ls();
	if len(objects)==0:
		print("No objects in scene")
		return
	for o in objects:
		if "gem" not in o:
			return o


#make gem geometry (one for now)
def makeGem():
	cmds.polyCube(name="gem")
	cmds.polyMoveEdge( 'gem.e[1:2]', s=(.75, .75, .75) )
	cmds.polyMoveEdge( 'gem.e[6:7]', s=(.75, .75, .75) )		#not sure this line is necessary
	cmds.polyMoveEdge( 'gem.e[1:2]', t=(0, -.5, 0) )

#place gem on a 
def placeGem(baseObj,gem):
	
	cmds.select('pCube1')

	# get UV bounding box
	bounds = cmds.polyEvaluate(b2 = True)
	print bounds
	gem_rows = [x for x in range(int(100*(bounds[1][1]-bounds[1][0])/.05)/100)]	#say gems are .05*.05 in uv space
	gem_cols = [x for x in range(int(100*(bounds[0][1]-bounds[0][0])/.05)/100)]

	to_place = getGemsToPlace(gem_rows, gem_cols)

def getGemsToPlace(rows, cols):
	#get UV points
	cmds.select(cmds.polyListComponentConversion('pCube1.vtx[*]',tuv = True))
	uvs = cmds.polyEditUV( query=True )

	uvs_to_check = makeConvexIshHull(uvs)

def makeConvexIshHull(uvs)
	angles = []
	anchor = (0,0)
	#select anchor point (max y value). should add a check here that uvs are loaded properly
	for u in range(1, len(uvs), 2):
		if uvs[u] == bounds[1][1]:
			anchor = (uvs[u-1], uvs[u])
			angles.append((u-1, 0))
			break

	print anchor

	#build list of tuples where x[0] = index in uv list, x[1] = angle with anchor
	for i in range(1, len(uvs)-1, 2):
		if i == u-1:	#anchor index
			continue
		pt = (uvs[i], uvs[i+1])
		angle_with_anchor = getAngle(anchor, pt)
		angles.append((i, angle_with_anchor))

	#sort by angle 
	sorted_angles = sorted(angles, key = lambda x: x[1])
	print sorted_angles



def getAngle(anchor, pt):
	vecX = (pt[0]-anchor[0])/ math.sqrt( (anchor[0] - pt[0])**2 + (anchor[1] - pt[1])**2 )
	#take dot prod with (1,0), which is just the x component.
	return math.acos(vecX)


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
