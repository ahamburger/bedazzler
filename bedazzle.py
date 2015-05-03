import maya.cmds as cmds
import maya.OpenMaya as OM
import math

def run(simplify, size, padding,shade):
	if not cmds.objExists(baseObject):
		cmds.textField("baseObject", e=True, tx="Please select a valid object.")
		return False
	makeGem(size)
	triangulateMesh(simplify)
	findPoints(size+padding)

	cmds.delete('gem')	#need to account for running script more than once maybe
	cmds.delete('triObj')
	cmds.group("gem*", name = "gems")

	if shade:
		throwShade()
	return True

#return first object in the scene (for now) except for gemstones
def pickBaseObject(selectedObject):
	if len(selectedObject) == 0:
		cmds.textField("baseObject", e=True, tx="Please select an object.")
	elif len(selectedObject) > 1:
		cmds.textField("baseObject", e=True, tx="Please select just one object.")
	elif not cmds.objExists(selectedObject[0]):
		cmds.textField("baseObject", e=True, tx="Please select a valid object.")
	else:
		global baseObject
		baseObject = selectedObject[0]
		cmds.textField("baseObject", e=True, tx=baseObject)

#make gem geometry (one for now)
def makeGem(size):
	#import gem
	if not cmds.objExists('gem'):
		cmds.file("gem.ma", i=True)

	cmds.select('gem')
	cmds.xform(s=(size,size,size))

def triangulateMesh(simplify):
	cmds.select(baseObject)
	cmds.duplicate(baseObject, name = "triObj")
	cmds.select('triObj')

	if simplify > 0:
		cmds.polyReduce(ver = 1, p = simplify)

	num_faces = cmds.polyEvaluate('triObj', f=True)
	
	#iterate over faces
	print "Triangulating faces..."
	for face_i in range(num_faces):		
		face = cmds.select('triObj.f['+ str(face_i)+']')		
		verts = getCorners(face_i)

		if not isCoplanar(verts):
			cmds.polyTriangulate('triObj.f['+ str(face_i)+']')

def getCorners(face_i):
	face = cmds.select('triObj.f['+ str(face_i)+']')
	verts = cmds.polyListComponentConversion(tv = True)

	cmds.select(verts)
	verts_f= cmds.filterExpand( ex=True, sm=31 )
	corners = []
	for vert_i in verts_f:
		cmds.select(vert_i)
		corners.append(cmds.xform(query=True, translation=True, worldSpace=True))
	return corners

def isCoplanar(verts):
	if len(verts) == 4:
		v1 = [verts[2][i] - verts[0][i] for i in range(0,3)]
		v2 = [verts[1][i] - verts[0][i] for i in range(0,3)]
		v3 = [verts[3][i] - verts[2][i] for i in range(0,3)]
		v2crossv3 = crossProd(v2,v3)
		return math.fabs(sum([v1[i] * v2crossv3[i] for i in range(0,3)])) <= .001
	return False

def findPoints(gem_dim):
	points = []
	normals = []
	
	cmds.select('triObj')
	num_faces = cmds.polyEvaluate('triObj', f=True)	
	print "Starting to iterate over faces..."
	for face_i in range(num_faces):
		if ((num_faces - face_i) % 5 == 0):
			print "Approximately " + str(num_faces - face_i) + " faces remaining...."
		
		cmds.select('triObj.f['+ str(face_i)+']')
		bounds = cmds.polyEvaluate(bc = True)
		normal = cmds.polyInfo(fn=True)
		corners = getCorners(face_i)

		avg = getAvg(corners)
		normal_f = normalize([float(i) for i in normal[0].split(':')[1].split()])
		
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

		#vectors for spiraling
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
				dir_vec = up
				#going right
				if case == 1:					
					dir_vec = right
				#going down
				elif case == 2:
					dir_vec = [-1*u for u in up]
				#going left
				elif case == 3:				
					dir_vec = [-1*r for r in right]

				curr_pt =  [temp[p] + gem_dim*dir_vec[p] for p in range(3)]

				if checkPt(curr_pt, bounds, corners):
					pts_to_check = []
					pts_to_check.append([curr_pt[p] + 0.5*gem_dim*up[p] for p in range(3)])
					pts_to_check.append([curr_pt[p] - 0.5*gem_dim*up[p] for p in range(3)])
					pts_to_check.append([curr_pt[p] + 0.5*gem_dim*right[p] for p in range(3)])
					pts_to_check.append([curr_pt[p] - 0.5*gem_dim*right[p] for p in range(3)])

					useSpot = True
					for p in pts_to_check:
						if useSpot:
							useSpot = checkPt(p, bounds, corners)

					if useSpot:
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

	print "Placing " + str(len(points)) + " gems..."
	for c in range(len(points)):
		placeGem(points[c],normals[c])


# check if point is within bounds of the face
# adapted from:
# http://bbs.dartmouth.edu/~fangq/MATH/download/source/Determining%20if%20a%20point%20lies%20on%20the%20interior%20of%20a%20polygon.htm
def checkPt(pt, bounds, verts):
	#want to check all extremes of gemstone. Add this once have better idea of gemstone shape

	#quick check that it's within the bounding box
	for i in range(3):
		if pt[i] < bounds[i][0] or pt[i] > bounds[i][1]:
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

	#angle sum approx equal to 2*pi-- should probably change this to be an epsilon value

	if anglesum >= 1.95*math.pi and anglesum <= 2.05*math.pi or (len(verts) > 3 and anglesum <= 3.05*math.pi):
		#not sure why quads need greater angle sum value. this seems wrong.
		return True
	return False


def placeGem(pt, norm):
	cmds.select('gem')
	cmds.instance()

	r_angle = getRotAngle(norm)
	cmds.rotate(r_angle[0],r_angle[1],r_angle[2], r = True)
	cmds.move(pt[0], pt[1], pt[2])

def throwShade():
	if not cmds.objExists('gem_shader'):
		cmds.file("shader.ma", i=True)

	cmds.select("gem*")
	cmds.hyperShade(a="gem_shader")

def getMagnitude(n):
	return math.sqrt(sum(n[i]* n[i] for i in range(len(n))))

#returns normalized cross product
def crossProd(a, b):
	v = [0,0,0]
	v[0] = a[1]*b[2] - a[2]*b[1]
	v[1] = a[2]*b[0] - a[0]*b[2]
	v[2] = a[0]*b[1] - a[1]*b[0]

	if v == [0.0,0.0,0.0]:
		return v
	return normalize(v)

def normalize(v):
	mag = getMagnitude(v)
	return [val/mag for val in v]

def getRotAngle(n):
	ret = []

	n = normalize(n)
	for val in n:
		new_val = math.degrees(math.acos(val))
		ret.append(new_val)

	new_ret = [ret[1], 90+ret[0], 0]
	if n[2]>0:
		new_ret[1] = 90-ret[0]

	return new_ret

def getAvg(corners):
	avg=[0,0,0]

	for p in corners:
		avg[0] += p[0]/len(corners)
		avg[1] += p[1]/len(corners)
		avg[2] += p[2]/len(corners)

	return avg
