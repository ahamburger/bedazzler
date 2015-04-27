import maya.cmds as cmds
import maya.OpenMaya as OM
import math

def run():
	base = pickBaseObject()
	g = makeGem()
	findSpots(base, g)

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
	cmds.polyCube(name="gem", w=.25, d=.25, h=.1)
	cmds.polyMoveEdge( 'gem.e[1:2]', s=(.75, .75, .75) )
	# cmds.polyMoveEdge( 'gem.e[6:7]', s=(.75, .75, .75) )		#not sure this line is necessary
	# cmds.polyMoveEdge( 'gem.e[1:2]', t=(0, -.5, 0) )


#place gem on a 
def findSpots(baseObj,gem):
	cmds.select('pCube1')
	centers = []
	normals = []
	for face_i in range(cmds.polyEvaluate('pCube1', f=True)):
		face = cmds.select('pCube1.f['+ str(face_i)+']')

		normal = cmds.polyInfo(fn=True)
		verts2 = cmds.polyListComponentConversion(tv = True)
		cmds.select(verts2)
		verts= cmds.filterExpand( ex=True, sm=31 )
		# print(verts)
		positions = []

		for vert_i in verts:#range(cmds.polyEvaluate(verts, v=True)):
			cmds.select(vert_i)#'pCube1.vtx['+ str(vert_i)+']')
			positions.append(cmds.xform(query=True, translation=True, worldSpace=True))
		
		avg=[0,0,0]

		for p in positions:
			avg[0] += p[0]/4
			avg[1] += p[1]/4
			avg[2] += p[2]/4

		normal_f = [float(i) for i in normal[0].split(':')[1].split()]
		
		placeGem(avg, normal_f,gem)

	# for c in range(len(centers)-1):	
	# 	print c
	# 	print centers[c]
	# 	print normals[c]	
	# 	placeGem(centers[c],normal[c],gem)

	cmds.delete('gem')

def placeGem(pt, norm, gem):
	cmds.select('gem')
	cmds.duplicate()

	r_angle = getRotAngle(norm)
	print r_angle
	cmds.rotate(r_angle[0],r_angle[1],r_angle[2])
	cmds.move(pt[0], pt[1], pt[2])

def getRotAngle(n):
	ret = []

	magnitude = math.sqrt(sum(n[i]* n[i] for i in range(len(n))))
	print magnitude
	for val in n:
		new_val = math.acos(val/magnitude) * 180 / math.pi
		ret.append(new_val)

	return ret
#not using this probably:
# script that returns the center point of selected polygon faces. 
# owen burgess 2009
# http://forums.cgsociety.org/archive/index.php/t-1034715.html

def faceCenter():

	faceCenter = []
	selection = OM.MSelectionList()
	OM.MGlobal.getActiveSelectionList(selection)
	iter = OM.MItSelectionList (selection, OM.MFn.kMeshPolygonComponent)

	while not iter.isDone():
		status = OM.MStatus
		dagPath = OM.MDagPath()
		component = OM.MObject()

		iter.getDagPath(dagPath, component)

		polyIter = OM.MItMeshPolygon(dagPath, component)

		while not polyIter.isDone():

			i = 0
			i = polyIter.index()
			faceInfo = [0]
			faceInfo[0] = ("The center point of face %s is:" %i)

			center = OM.MPoint
			center = polyIter.center(OM.MSpace.kWorld)
			point = [center.x,center.y,center.z]

			faceCenter.append(point)

			polyIter.next()

		iter.next()

	return faceCenter

	"""
	THE NEW PLAN:
	Iterate over faces
	Find midpoint of each faces
		Place gem
	Spiral around that midpoint, placing gems using a vector that lies in the plane (perpendicular to an edge? random?)
	fin.

	"""
