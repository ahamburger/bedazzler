import maya.cmds as cmds
import maya.OpenMaya as OM
import math

def run(isObj, simplify, size, padding,shade, smoothe, overlap):
	if not cmds.objExists(baseObject):
		cmds.textField("baseObject", e=True, tx="Please select a valid object.")
		return False
	makeGem(size)
	triangulated = triangulateMesh(isObj,simplify, smoothe)

	# if overlap is 0, want .5. if overlap is 1, want 1
	overlap = .5*(1.0-overlap)
	findPoints(isObj, size,padding, overlap)

	cmds.delete('gem')	#need to account for running script more than once maybe
	if isObj:
	 	cmds.delete('triObj')

	# if cmds.objExists('gem*'):
	cmds.group("gem*", name = "gems")

	if shade:
		throwShade()
	return True

#does not work if changing base object to run script again
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

#make gem geometry
def makeGem(size):
	#import gem
	if not cmds.objExists('gem'):
		cmds.file("gem.ma", i=True)

	cmds.select('gem')
	cmds.xform(s=(size,size,size))

def triangulateMesh(isObj, simplify, smoothe):
	if isObj: 
		cmds.select(baseObject)
		cmds.duplicate(baseObject, name = "triObj")
		cmds.select('triObj')

		if smoothe:
			cmds.polySmooth('triObj', c=smoothe)
			cmds.polyReduce(ver = 1)
			cmds.polyReduce(ver = 1)

		if simplify > 0:
			cmds.polyReduce(ver = 1, p = simplify)

		num_faces = cmds.polyEvaluate('triObj', f=True)
		
		print "Triangulating faces..."
		#iterate over faces
		face_i = 0
		while face_i < num_faces:
			if ((num_faces - face_i) % 5 == 0):
				print "Triangulate check: Approximately " + str(num_faces - face_i) + " faces remaining...."
			face = cmds.select('triObj.f['+ str(face_i)+']')		
			verts = getCorners(isObj,face_i)
			if not isCoplanar(verts):
				cmds.polyTriangulate('triObj.f['+ str(face_i)+']')
				num_faces = cmds.polyEvaluate('triObj', f=True)
			face_i +=1


def findPoints(isObj, gem_dim, padding, overlap):
	points = []
	normals = []
	
	cmds.select(baseObject)
	num_faces = 1
	if isObj:
		cmds.select('triObj')
		num_faces = cmds.polyEvaluate('triObj', f=True)	
	print "Starting to iterate over " + str(num_faces) + " faces..."
	for face_i in range(num_faces):
		if ((num_faces - face_i) % 5 == 0):
			print "Approximately " + str(num_faces - face_i) + " faces remaining...."
		if isObj:
			cmds.select('triObj.f['+ str(face_i)+']')

		bounds = cmds.polyEvaluate(bc = True)
		normal = cmds.polyInfo(fn=True)
		corners = getCorners(isObj,face_i)
		edges = getEdges(isObj,face_i)
		cmds.select(baseObject)


		avg = getAvg(corners)
		normal_f = normalize([float(i) for i in normal[0].split(':')[1].split()])

		#vectors for spiraling				
		up = findUpVector(normal_f)
		right = normalize(crossProd(normal_f, up))

		if checkWholeGem(avg, bounds, corners, gem_dim, up, right, edges, overlap):
			points.append(avg)
			normals.append(normal_f)

			hit_bound = [0,0,0,0,0,0]
			curr_pt = avg
			count = 0
			sub_count_goal = 0
			
			#check to see if we've hit any bounds
			for i in range(3):
				if curr_pt[i] <= bounds[i][0] + .000001: 
					hit_bound[2*i] = 1
				if curr_pt[i] >= bounds[i][1] - .000001:
					hit_bound[2*i+1] = 1

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

					curr_pt =  [temp[p] + (gem_dim+padding)*dir_vec[p] for p in range(3)]

					if checkWholeGem(curr_pt, bounds, corners, gem_dim, up, right, edges, overlap):
						points.append(curr_pt)
						normals.append(normal_f)

					sub_count +=1
			
					#check to see if we've hit any bounds
					for i in range(3):
						if curr_pt[i] <= bounds[i][0]+ .000001: 
							hit_bound[2*i] = 1
						if curr_pt[i] >= bounds[i][1]- .000001:
							hit_bound[2*i+1] = 1
				
				count += 1

				if case == 1 or case == 3:
					sub_count_goal += 1
					up_switch = not up_switch

	print "Placing " + str(len(points)) + " gems..."
	for c in range(len(points)):
		placeGem(points[c],normals[c])

def checkWholeGem(midpt, bounds, corners, gem_dim, up, right, edges, overlap):
	pts_to_check = []
	if checkPt(midpt, bounds, corners, edges):
		pts_to_check.append([midpt[p] + overlap*gem_dim*up[p] for p in range(3)])			#could add a "sensitivity" variable that affects how far out this checks, could also add option of starting at corner or in the middle of face
		pts_to_check.append([midpt[p] - overlap*gem_dim*up[p] for p in range(3)])
		pts_to_check.append([midpt[p] + overlap*gem_dim*right[p] for p in range(3)])
		pts_to_check.append([midpt[p] - overlap*gem_dim*right[p] for p in range(3)])

		useSpot = True
		for p in pts_to_check:
			if useSpot:
				useSpot = checkPt(p, bounds, corners, edges)
	 	return useSpot
	return False				


# check if point is within bounds of the face
def checkPt(pt, bounds, verts, edges):
 	if len(verts)>3:		#should support verts>4?
 		if makeDiag(verts[0], verts[3], edges):
   			return (checkTriangle(verts[:3], pt) or checkTriangle(verts[1:], pt))
   		if makeDiag(verts[1], verts[3], edges):
   			return (checkTriangle(verts[:3], pt) or checkTriangle([verts[0],verts[2],verts[3]], pt))
   		if makeDiag(verts[2], verts[3], edges):
   			return (checkTriangle(verts[:3], pt) or checkTriangle([verts[0],verts[1],verts[3]], pt))

   	return checkTriangle(verts, pt)

# adapted from:
# http://bbs.dartmouth.edu/~fangq/MATH/download/source/Determining%20if%20a%20point%20lies%20on%20the%20interior%20of%20a%20polygon.htm
def checkTriangle(verts, pt):
	anglesum = 0
	costheta = 0

   	eps = 0.0001
   	for i in range(len(verts)):
		p1 = [verts[i][j]- pt[j] for j in range(3)]
		p2 = [verts[(i+1)%len(verts)][j]- pt[j] for j in range(3)]
		
		m1 = getMagnitude(p1)
		m2 = getMagnitude(p2)

		if (m1*m2 <= eps):
			return True

		p1 = normalize(p1)
		p2 = normalize(p2)

		if [-1*p for p in p1] == p2:
			return True

		costheta = sum([p1[i]*p2[i] for i in range(3)])
		costheta = min(1.0,max(costheta,-1.0))

		anglesum += math.acos(costheta)

	#angle sum approx equal to 2*pi
	if math.fabs(2*math.pi-anglesum) <= eps:
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

def getCorners(isObj, face_i):
	if isObj:
		face = cmds.select('triObj.f['+ str(face_i)+']')
	else:
		face = cmds.select(baseObject)
	verts = cmds.polyListComponentConversion(tv = True)

	cmds.select(verts)
	verts_f= cmds.filterExpand( ex=True, sm=31 )
	corners = []
	for vert_i in verts_f:
		cmds.select(vert_i)
		corners.append(cmds.xform(query=True, translation=True, worldSpace=True))
	return corners

def getEdges(isObj, face_i):
	e_verts = []
	if isObj:
		face = cmds.select('triObj.f['+ str(face_i)+']')
	else:
		face = cmds.select(baseObject)
	edges = cmds.polyListComponentConversion(te = True)
	cmds.select(edges)
	edges_f= cmds.filterExpand( ex=True, sm=32 )
	for e in edges_f:
		cmds.select(e)
		verts = cmds.polyListComponentConversion(tv = True)
		cmds.select(verts)
		verts_f= cmds.filterExpand( ex=True, sm=31 )
		pair = []
		for vert_i in verts_f:
			cmds.select(vert_i)
			pair.append(cmds.xform(query=True, translation=True, worldSpace=True))
		e_verts.append(pair)

	return e_verts

def isCoplanar(verts):
	if len(verts) == 4:
		v1 = [verts[2][i] - verts[0][i] for i in range(0,3)]
		v2 = [verts[1][i] - verts[0][i] for i in range(0,3)]
		v3 = [verts[3][i] - verts[2][i] for i in range(0,3)]
		v2crossv3 = crossProd(v2,v3)
		return math.fabs(sum([v1[i] * v2crossv3[i] for i in range(0,3)])) <= .01
	return False

def findUpVector(normal_f):
	#finding vector perpendicular to normal that lies in the plane between the normal and y axis (0,1,0)
	#this can be simplified if it works
	#unless normal is already the y axis, then use the z axis as "up"
	neg_n = normalize([-1*n for n in normal_f])
	if normal_f == [0.0,1.0,0.0] or normal_f == [0.0,-1.0,0.0]:
		up = [-1*neg_n[2]*neg_n[0], -1*neg_n[2]*neg_n[1],1-neg_n[2]*neg_n[2]]
	else:
		up = [-1*neg_n[1]*neg_n[0], 1-neg_n[1]*neg_n[1],-1*neg_n[1]*neg_n[2]]
	return normalize(up)

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
	#projection onto xz plane-- n - ndot(0,1,0)*(0,1,0)
	xz_proj = [n[0],0.0,n[2]]
	if not xz_proj == [0.0,0.0,0.0]:
		xz_proj = normalize(xz_proj)

	proj_angle = math.degrees(math.acos(xz_proj[0]))

	rangles = [math.degrees(math.acos(n[1])), 90+proj_angle, 0]
	if n[2] >0:
		rangles[1] = 90-proj_angle
	return rangles

def getAvg(corners):
	avg=[0.0,0.0,0.0]

	for p in corners:
		avg[0] += p[0]/len(corners)
		avg[1] += p[1]/len(corners)
		avg[2] += p[2]/len(corners)
		
	return avg

def makeDiag(v1, v2, edges):
	for e in edges:
		if e == [v1, v2] or e == [v2,v1]:
			return False
	return True