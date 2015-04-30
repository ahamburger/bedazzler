import maya.cmds as cmds
import maya.OpenMaya as OM
import math

def run():
	base = pickBaseObject()
	g = makeGem()
	findPoints(base, g)

	cmds.delete('gem')
	cmds.group("gem*", name = "gems")

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
	cmds.polyCube(name="gem", w=.25, d=.25, h=.05)
	cmds.polyMoveEdge( 'gem.e[1:2]', s=(.75, .75, .75) )
	# cmds.polyMoveEdge( 'gem.e[6:7]', s=(.75, .75, .75) )		#not sure this line is necessary
	# cmds.polyMoveEdge( 'gem.e[1:2]', t=(0, -.5, 0) )


#place gem on a 
def findPoints(baseObj,gem):

	gem_dim = .75*.25+.02

	cmds.select('pCube1')
	cmds.polyTriangulate()
	points = []
	normals = []

	for face_i in range(cmds.polyEvaluate('pCube1', f=True)):
		face = cmds.select('pCube1.f['+ str(face_i)+']')
		bounds = cmds.polyEvaluate(bc = True)

		normal = cmds.polyInfo(fn=True)
		verts = cmds.polyListComponentConversion(tv = True)
		cmds.select(verts)
		verts_f= cmds.filterExpand( ex=True, sm=31 )

		corners = []
		for vert_i in verts_f:
			cmds.select(vert_i)
			corners.append(cmds.xform(query=True, translation=True, worldSpace=True))
		
		avg=[0,0,0]

		for p in corners:
			avg[0] += p[0]/len(corners)
			avg[1] += p[1]/len(corners)
			avg[2] += p[2]/len(corners)

		normal_f = [float(i) for i in normal[0].split(':')[1].split()]
		
		points.append(avg)
		normals.append(normal_f)

		hit_bound = [0,0,0,0,0,0]
		curr_pt = avg
		
		#finding vector perpendicular to normal that lies in the plane between the normal and y axis (0,1,0)
		#this can be simplified if it works
		#unless normal is already the y axis, then use the z axis as "up"
		neg_n = normalize([-1*n for n in normal_f])
		if normal_f == [0.0,1.0,0.0] or normal_f == [0.0,-1.0,0.0]:
			up = [-1*neg_n[2]*neg_n[0], -1*neg_n[2]*neg_n[1],1-neg_n[2]*neg_n[2]]
		else:
			up = [-1*neg_n[1]*neg_n[0], 1-neg_n[1]*neg_n[1],-1*neg_n[1]*neg_n[2]]

		up = normalize(up)

		right = normalize(crossProd(normal_f, up))
		count = 0
		sub_count_goal = 0
		while sum(hit_bound)<6:		#while we haven't hit all 6 bounds, keep looking for points
			case = count % 4
			sub_count = 0

			up_switch = False

			while sub_count < sub_count_goal:
				temp = curr_pt
				#going up
				if case == 0:
					curr_pt = [temp[p] + gem_dim*up[p] for p in range(3)]
				#going right
				elif case == 1:					
					curr_pt = [temp[p] + gem_dim*right[p] for p in range(3)]
				#going down
				elif case == 2:
					curr_pt = [temp[p] - gem_dim*up[p] for p in range(3)]
				#going left
				else:				
					curr_pt = [temp[p] - gem_dim*right[p] for p in range(3)]
				
				if checkPt(curr_pt, bounds, corners):
					points.append(curr_pt)
					normals.append(normal_f)

				sub_count +=1
			
			count += 1

			if case == 1 or case == 3:
				sub_count_goal += 1
				up_switch = not up_switch

			#check to see if we've hit any bounds
			for i in range(3):
				if curr_pt[i] <= bounds[i][0]: 
					hit_bound[2*i] = 1
				if curr_pt[i] >= bounds[i][1]:
					hit_bound[2*i+1] = 1

	for c in range(len(points)):
		placeGem(points[c],normals[c],gem)


# check if point is within bounds of the face
# adapted from:
# http://bbs.dartmouth.edu/~fangq/MATH/download/source/Determining%20if%20a%20point%20lies%20on%20the%20interior%20of%20a%20polygon.htm
def checkPt(pt, bounds, verts):
	#quick check that it's within the bounding box
	for i in range(3):
		if pt[i] < bounds[i][0]:
			return False
		if pt[i] > bounds[i][1]:
			return False
	anglesum = 0
	costheta = 0

   	eps = 0.000001
   	for i in range(len(verts)):
		p1 = [0,0,0]
		p2 = [0,0,0]
		p1[0] = verts[i][0] - pt[0]
		p1[1] = verts[i][1] - pt[1]
		p1[2] = verts[i][2] - pt[2]
		p2[0] = verts[(i+1)%len(verts)][0] - pt[0]
		p2[1] = verts[(i+1)%len(verts)][1] - pt[1]
		p2[2] = verts[(i+1)%len(verts)][2] - pt[2]

		m1 = getMagnitude(p1)
		m2 = getMagnitude(p2)
		if (m1*m2 <= eps):
			return True

		costheta = (p1[0]*p2[0] + p1[1]*p2[1] + p1[2]*p2[2])/(m1*m2)
		costheta = min(1,max(costheta,-1))
		anglesum += math.acos(costheta)

	#angle sum approx equal to 2*pi
	if anglesum >= 1.95*math.pi and anglesum <= 2.05*math.pi:
		return True
	return False


def placeGem(pt, norm, gem):
	cmds.select('gem')
	cmds.instance()

	r_angle = getRotAngle(norm)
	cmds.rotate(r_angle[0],r_angle[1],r_angle[2], r = True)
	cmds.move(pt[0], pt[1], pt[2])


def getMagnitude(n):
	return math.sqrt(sum(n[i]* n[i] for i in range(len(n))))

#returns normalized cross product
def crossProd(a, b):
	v = [0,0,0]
	v[0] = a[1]*b[2] - a[2]*b[1]
	v[1] = a[2]*b[0] - a[0]*b[2]
	v[2] = a[0]*b[1] - a[1]*b[0]

	return normalize(v)

def normalize(v):
	mag = getMagnitude(v)
	return [val/mag for val in v]

def getRotAngle(n):
	ret = []

	n = normalize(n)	#may already be normalized but doesn't hurt
	for val in n:
		new_val = math.degrees(math.acos(val))
		ret.append(new_val)

	new_ret = [ret[1], 90+ret[0], 0]
	if n[2]>0:
		new_ret[1] = 90-ret[0]

	return new_ret


	"""
	THE NEW PLAN:
	Iterate over faces
	Find midpoint of each faces
		Place gem
	Spiral around that midpoint, placing gems using a vector that lies in the plane (perpendicular to an edge? random?)
	fin.

	"""
