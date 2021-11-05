import bpy, bmesh, os, random
from collections import defaultdict
from math import atan, pi, radians
import math
import random

def deleteEverything():
    ob1 = bpy.context.scene.objects["Camera"]
    ob2 = bpy.context.scene.objects["Light"]    

    #Select everything except camera and light
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = ob1   
    ob1.select_set(False)
    bpy.context.view_layer.objects.active = ob2   
    ob2.select_set(False)
    
    #Delete everything
    bpy.ops.object.delete(use_global=False, confirm=False)

def scaleSizes():
    global wireWidth
    global solderingSurfaceRadius
    global holeRadius
    global sizeScale
    
    #Reset sizes
    wireWidth /= sizeScale
    solderingSurfaceRadius /= sizeScale
    holeRadius /= sizeScale
    
    #Scale sizes
    #Generate new factor
    sizeScale = random.uniform(1, 1.4)
    
    wireWidth *= sizeScale
    solderingSurfaceRadius *= sizeScale
    holeRadius *= sizeScale
        
def createMaterials():
    #Create hole material
    materialHole = bpy.data.materials.new("Hole")
    materialHole.diffuse_color = (0,0,0,1)
    
    #Create hole clogging material
    materialHoleClogging = bpy.data.materials.new("HoleClogging")
    materialHoleClogging.diffuse_color = (0.8,0.8,0.8,1)
    
    #Create surface material
    mat = bpy.data.materials.new(name="Surface")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(path+"Materials\\surface.png")
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    
    #Create wire material
    mat = bpy.data.materials.new(name="Wire")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(path+"Materials\\wire.png")
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])  
    
def assignMaterial(color, obj):
	#Select proper material
    mat = bpy.data.materials.get(color)
	#Assign it to the object
    obj.active_material = mat
    
def setLight():
    #Set light parameters
    bpy.data.objects['Light'].data.type = 'AREA'
    bpy.data.objects['Light'].location[0] = 0
    bpy.data.objects['Light'].location[1] = 0
    bpy.data.objects['Light'].location[2] = 5
    bpy.data.objects['Light'].rotation_euler[0] = 0
    bpy.data.objects['Light'].rotation_euler[1] = 0
    bpy.data.objects['Light'].rotation_euler[2] = 0
    bpy.data.objects['Light'].scale[0] = 200
    bpy.data.objects['Light'].scale[1] = 200
    bpy.data.objects['Light'].data.energy = 1000
    
def setCamera():
    #Set camera postiton
    objCamera = bpy.data.objects.get("Camera")
    objCamera.rotation_euler[0] = 0
    objCamera.rotation_euler[1] = 0
    objCamera.rotation_euler[2] = 0
    objCamera.location[0] = 0
    objCamera.location[1] = 0
    objCamera.location[2] = 27.778

def pointGenerator():
    #Determine the difference of the points according to number of wires
    pointDiff = surfaceSize / (2 * numOfWires)
    
    for i in range(numOfWires):
        # x0 can be the following, if surfaceSize is 20
        # 3 lines: -6.66, 0, 6.66
        # 2 lines: -5, 5
        # 1 lines: 0 
        #Scale i to 1,3,5
        scaleFactor = (i * 2 + 1) 
        maxSpace = pointDiff - wireWidth
        
        #5 is a magic number
        y0Max = surfaceSize - 1 - maxSpace - solderingSurfaceRadius - 5 * wireWidth
        y1Max = surfaceSize - 1 - maxSpace
        
        x0 = pointDiff * scaleFactor - surfaceSize/2
        y0 = random.uniform(1, y0Max) -	surfaceSize/2
            
        x1 = x0
        y1 = random.uniform(y0 + solderingSurfaceRadius + wireWidth + surfaceSize/2, y1Max) - surfaceSize/2
        
        #Branch direction
        # -1 left, 0 straight, 1 right
        direction = random.randint(-1, 1)
        
        if (direction == 0):
            x2 = x1
            y2 = surfaceSize/2
            #Put into points array
            points = [(x0, y0, 0.0), (x1, y1, 0.0), (x2, y2, 0.0)]
        else:
            maxBranch = maxSpace * math.sqrt(2)
            #Generate length of branch
            branchLength = random.uniform(math.sqrt(2), maxBranch)
            x2 = x1 + direction * branchLength / math.sqrt(2)
            y2 = y1 + branchLength / math.sqrt(2)  
                  
            x3 = x2
            y3 = surfaceSize/2
            #Put into points array
            points = [(x0, y0, 0.0), (x1, y1, 0.0), (x2, y2, 0.0), (x3, y3, 0.0)]
        
        wirePoints.append(points)

def calculateHolePositionErrors():
    for i in range(numOfWires):
        #50% chance of hole position error
        if(random.randint(0, 1) == 0):
			#Set maximum and minimum of the radius
            r1 = (solderingSurfaceRadius - holeRadius)*0.5
            r2 = solderingSurfaceRadius - holeRadius
            
			#Generate radius
            R = random.uniform(r1, r2)
            
			#Generate x coordinate
            x = random.uniform(-R, R)
			
			#Calculate y coordinate from x and R
            y = random.choice([-1, 1]) * math.sqrt(R*R-x*x)
            
            #Write to annotation file
            write2AnnotationFile(wirePoints[i][0][0],wirePoints[i][0][1],solderingSurfaceRadius,HOLE_POSITION_ERROR_ID) 
        else:
			#No hole position error
            x = 0
            y = 0
        
		#Store coordinates to array
        xy = (x,y)
        holePositionErrors.append(xy)

def write2AnnotationFile(X,Y,objectSize,classId):
	#Transform coordinates
    X,Y = transformXY(X,Y)
	
	#Calculate scale factor and offset
    scaleFactor = imageMaxSize / surfaceSize
    offset = imageMaxSize / 2
	
	#Calculate x and y in image coordinate system
    x = int(scaleFactor * X + offset)
    y = int(-scaleFactor * Y + offset)    
	
	#Saturate results, defensive coding
    if (x > imageMaxSize):
        x = imageMaxSize        
    if (y > imageMaxSize):
        y = imageMaxSize
		
	#Calculate relative x and y center
    x_center = x/imageMaxSize
    y_center = y/imageMaxSize
	
	#Calculate width and height
    #0.2 object size is 0.4
    width = 2*objectSize/surfaceSize
    height = 2*objectSize/surfaceSize
	
    #Formating float precision    
    x_center = format(x_center,'.6f')
    y_center = format(y_center,'.6f')
    width = format(width,'.6f')
    height = format(height,'.6f')
	
    #Write into .txt
    string = str(classId)+" "+str(x_center)+" "+str(y_center)+" "+str(width)+" "+str(height)
    outF.write(string)
    outF.write("\n")

def transformXY(x,y):
    #Calculate the transformed X and Y with transformation matrix
    transformedX = x*math.cos(-rotate*1.5708)-y*math.sin(-rotate*1.5708)
    transformedY = x*math.sin(-rotate*1.5708)+y*math.cos(-rotate*1.5708)
    return transformedX,transformedY

def createSurface():
    #Add surface
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, -0.001), scale=(1, 1, 1))
    bpy.context.object.name = "Surface"
    bpy.context.object.scale[1] = surfaceSize/2
    bpy.context.object.scale[0] = surfaceSize/2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    objSurface = bpy.data.objects.get("Surface")
    
    #Assign material
    assignMaterial("Surface", objSurface)

def createWires():
    #Create plane for wires
    createTemplatePlane()
	
    for i in range(numOfWires):
        #Create wires
        createWireBetweenPoints(wirePoints[i])

def createWireBetweenPoints(points):
    #Create object for wire
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.context.object.name = "Line"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    objLine = bpy.data.objects.get("Line")
    
    #Connect points
    drawLines(points, objLine)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.convert(target='CURVE')
    
    bpy.context.object.data.dimensions = '2D'

    #Apply the template on line object
    objLine.data.bevel_mode = 'OBJECT'
    objLine.data.bevel_object = bpy.data.objects["TemplatePlane"]

    #Assign material
    assignMaterial("Wire", objLine)
        
def createTemplatePlane():
    #Create the template plane objct
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(15, 0, 0), scale=(1, 1, 1))
    bpy.context.object.name = "TemplatePlane"
    bpy.context.object.scale[1] = 0.001
	
    #Width of the wire
    bpy.context.object.scale[0] = wireWidth
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.convert(target='CURVE')

def addWireBreaks():    
    for i in range(numOfWires):
        #Decide which wire break will be added
		k = random.randint(0, 3)
        if(k == 0):
            createWireBreak(wirePoints[i], wireBreakShape0)
        elif(k == 1):
            createWireBreak(wirePoints[i], wireBreakShape1)
        elif(k == 2):
            createWireBreak(wirePoints[i], wireBreakShape2)
        else:
            createWireBreak(wirePoints[i], wireBreakShape3)			

def createWireBreak(points, pointsShape):
    #50% chance of wire break
    if (random.randint(0, 1) == 1):
		#Create proper wire break type
        createShape(pointsShape)
        
        #Choose 2 points where to generate wire break
        i = random.randint(0, len(points)-2)
        
        #Calculate direction of the wire break in degree
        degrees = calculateDirection(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
		
		#Convert degree to radians
        radians = math.radians(degrees)
        bpy.context.object.rotation_euler[2] = radians
        
        #Set size of the wire break
        bpy.context.object.scale[0] = wireWidth
        bpy.context.object.scale[1] = wireWidth

        #Set coordinate
        #If wire break is next to the hole, y0 has to be greater
        if (i ==0):
            x,y = generateXY(points[i][0],points[i][1] + solderingSurfaceRadius + wireWidth/2,points[i+1][0],points[i+1][1])
        else:
            x,y = generateXY(points[i][0],points[i][1],points[i+1][0],points[i+1][1])
            
        bpy.context.object.location[0] = x
        bpy.context.object.location[1] = y
        
        #Write to .txt
        write2AnnotationFile(x,y,wireWidth,WIRE_BREAK_ERROR_ID)


def createShape(pointsShape):
    #Create shape object for wire
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0.02), scale=(1, 1, 1))
    bpy.context.object.name = "Shape"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    objShape = bpy.context.object
    
    #Connect points
    drawLines(pointsShape, objShape)
    
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.edge_face_add()
	
    #Assign material
    assignMaterial("Surface", bpy.context.object)
    bpy.ops.object.mode_set(mode='OBJECT')
            
def drawLines(points, obj):
    bm = bmesh.from_edit_mesh(obj.data)
    
    #Store verts into "v" list
    v = defaultdict(list)
    for i in range(len(points)):
        vtemp = bm.verts.new(points[i])
        v[""].append(vtemp)

    #Create edges from the the "v" list
    for i in range(len(v[""])-1):
        bm.edges.new((v[""][i], v[""][i+1]))    
         
    bmesh.update_edit_mesh(obj.data)

def calculateDirection(x1, y1, x2, y2):
	#When wire is straight
    if (x1 == x2):
        k = random.randint(0, 1)
        return 90 + k*180
    else:
		#When wire is a curve
        direction = atan((y1-y2)/(x1-x2)) * 180 / pi
		
        k = random.randint(0, 1)
        if (direction < 0):
            return direction + 180 + k*180
        else:
            return direction + k*180

def generateXY(x1,y1,x2,y2):
    if (abs(x1 - x2) > abs(y1 - y2)):
        #Generate x coordinate of wire break
        x = random.uniform(x1, x2)      
        #Calculate y coordinate from x 
        y = calculate_y(x1, y1, x2, y2, x)
    else:
        #Generate y coordinate of wire break
        y = random.uniform(y1, y2)      
        #Calculate x coordinate from y 
        x = calculate_x(x1, y1, x2, y2, y)        
    return x,y  

#Calculate y from x
def calculate_y(x1, y1, x2, y2, x):
    y = y1+(y2-y1)*(x-x1)/(x2-x1)
    return y

#Calculate x from y
def calculate_x(x1, y1, x2, y2, y):
    x = x1+(x2-x1)*(y-y1)/(y2-y1)
    return x

def createSolderingSurfaces():
    for i in range(numOfWires):
        #Add object
        bpy.ops.mesh.primitive_cylinder_add(radius=solderingSurfaceRadius, depth=0.001, enter_editmode=False, align='WORLD', location=(wirePoints[i][0][0], wirePoints[i][0][1], 0.0015), scale=(1, 1, 1))
        bpy.context.object.name = "SolderingSurface"+str(i)
        bpy.context.object.scale[1] = 1
        bpy.context.object.scale[0] = 1
            
        #Assign material
        objSolderingSurface = bpy.data.objects.get("SolderingSurface"+str(i))
        assignMaterial("Wire", objSolderingSurface)
        
def createHoles():
    for i in range(numOfWires):
        #Add object
        bpy.ops.mesh.primitive_cylinder_add(radius=holeRadius, depth=0.001, enter_editmode=False, align='WORLD', location=(wirePoints[i][0][0] + holePositionErrors[i][0], wirePoints[i][0][1] + holePositionErrors[i][1], 0.0025), scale=(1, 1, 1))
        bpy.context.object.name = "Hole"+str(i)
        bpy.context.object.scale[1] = 1
        bpy.context.object.scale[0] = 1
            
        #Assign material
        objHole = bpy.data.objects.get("Hole"+str(i))
        assignMaterial("Hole", objHole)
        
def addHoleCloggings():
    for i in range(numOfWires):
        #50% chance of hole clogging
        if(random.randint(0, 1) == 0):
            #Add object
            bpy.ops.mesh.primitive_cylinder_add(radius=holeRadius, depth=0.001, enter_editmode=False, align='WORLD', location=(wirePoints[i][0][0] + holePositionErrors[i][0], wirePoints[i][0][1] + holePositionErrors[i][1], 0.0035), scale=(1, 1, 1))
            bpy.context.object.name = "HoleClogging"+str(i)
            bpy.context.object.scale[1] = 1
            bpy.context.object.scale[0] = 1
            
            #Assign material
            objHoleClogging = bpy.data.objects.get("HoleClogging"+str(i))
            assignMaterial("HoleClogging", objHoleClogging)
            
            #Write to annotation file
            write2AnnotationFile(wirePoints[i][0][0] + holePositionErrors[i][0],wirePoints[i][0][1] + holePositionErrors[i][1],holeRadius,HOLE_CLOGGING_ERROR_ID)

def renderModel():
    #Check if path is valid
    if os.path.exists(path):
		#Set file name
        bpy.context.scene.render.filepath = path+'Dataset\\model'+str(pictureNumber)+'.jpg'
		
		#Set resolution
        bpy.context.scene.render.resolution_x = imageMaxSize
        bpy.context.scene.render.resolution_y = imageMaxSize
		
		#Render
        bpy.ops.render.render(write_still=True)
    else:
        print("Wrong path")   
                                       
#INPUT PARAMETERS
#Path for dataset and materials
path = "C:\\Users\\Gergő\\Desktop\\BME\\Msc\\3. félév\\Diploma\\"
#Number of pictures
numOfPictures = 10
#Maximum number of wires
maxWires = 6
#Surface size
surfaceSize = 20
#Wire, hole and soldering surface size
wireWidth = 0.2
solderingSurfaceRadius = 0.75
holeRadius = 0.5
#Size modifier factor
sizeScale = 1
#Image resolution
imageMaxSize = 1080

#IDs for error types
HOLE_POSITION_ERROR_ID = 0
WIRE_BREAK_ERROR_ID = 1
HOLE_CLOGGING_ERROR_ID = 2

#Possible wire break types
wireBreakShape0 = [(1.0,1.0,0.0),(1.0,-1.0,0.0),(-1.0,-1.0,0.0),(-1.0,1.0,0.0)]
wireBreakShape1 = [(-0.44056040048599243,0.9923735857009888,0.0), (-0.37828749418258667,0.9923735857009888,0.0), (-0.284443736076355,0.9923735857009888,0.0), (-0.1653432846069336,0.9923735857009888,0.0), (-0.027300313115119934,0.9923735857009888,0.0), (0.12337100505828857,0.9923735857009888,0.0), (0.2803564965724945,0.9923735857009888,0.0), (0.43734198808670044,0.9923735857009888,0.0), (0.5880132913589478,0.9923735857009888,0.0), (0.7260562777519226,0.9923735857009888,0.0), (0.845156729221344,0.9923735857009888,0.0), (0.9390004873275757,0.9923735857009888,0.0), (1.0012736320495605,0.9923735857009888,0.0), (0.9885700941085815,0.9593090415000916,0.0), (0.962232232093811,0.9055152535438538,0.0), (0.9248384237289429,0.8352116942405701,0.0), (0.8789671063423157,0.7526178359985352,0.0), (0.8271965980529785,0.6619531512260437,0.0), (0.77210533618927,0.5674371123313904,0.0), (0.7162717580795288,0.47328925132751465,0.0), (0.662274181842804,0.3837289810180664,0.0), (0.6126910448074341,0.3029758036136627,0.0), (0.570100724697113,0.23524919152259827,0.0), (0.5370815992355347,0.18476863205432892,0.0), (0.5162120461463928,0.15575364232063293,0.0), (0.4614240527153015,0.09101337194442749,0.0), (0.40359848737716675,0.026070058345794678,0.0), (0.34289294481277466,-0.038498036563396454,0.0), (0.2794649600982666,-0.10211264342069626,0.0), (0.2134721279144287,-0.1641954928636551,0.0), (0.14507202804088593,-0.2241683304309845,0.0), (0.07442222535610199,-0.28145289421081543,0.0), (0.0016802921891212463,-0.33547088503837585,0.0), (-0.07299619168043137,-0.3856440484523773,0.0), (-0.1494496464729309,-0.43139412999153137,0.0), (-0.22752252221107483,-0.47214287519454956,0.0), (-0.3070572018623352,-0.5073120594024658,0.0), (-0.35896116495132446,-0.5280007719993591,0.0), (-0.40206748247146606,-0.5448148250579834,0.0), (-0.4377216100692749,-0.5581926703453064,0.0), (-0.46726903319358826,-0.5685728192329407,0.0), (-0.4920552372932434,-0.576393723487854,0.0), (-0.5134257078170776,-0.5820938944816589,0.0), (-0.5327259302139282,-0.5861117839813232,0.0), (-0.5513014197349548,-0.5888859033584595,0.0), (-0.5704975724220276,-0.5908547043800354,0.0), (-0.5916599631309509,-0.5924566984176636,0.0), (-0.6161340475082397,-0.5941303968429565,0.0), (-0.6452652215957642,-0.5963141918182373,0.0), (-0.6426652669906616,-0.5318052172660828,0.0), (-0.6353951096534729,-0.4457327425479889,0.0), (-0.6242491602897644,-0.34242069721221924,0.0), (-0.6100218892097473,-0.22619304060935974,0.0), (-0.5935077667236328,-0.10137371718883514,0.0), (-0.5755012035369873,0.027713298797607422,0.0), (-0.5567967295646667,0.1567440629005432,0.0), (-0.5381887555122375,0.2813946008682251,0.0), (-0.5204718112945557,0.39734095335006714,0.0), (-0.5044403076171875,0.5002591609954834,0.0), (-0.49088868498802185,0.5858253240585327,0.0), (-0.4806113839149475,0.6497154235839844,0.0), (-0.4779691994190216,0.6705268025398254,0.0), (-0.47543078660964966,0.6983524560928345,0.0), (-0.4729270935058594,0.7315105199813843,0.0), (-0.47038906812667847,0.7683190703392029,0.0), (-0.46774762868881226,0.8070961236953735,0.0), (-0.46493369340896606,0.846159815788269,0.0), (-0.4618782103061676,0.8838282227516174,0.0), (-0.4585121273994446,0.9184194207191467,0.0), (-0.4547663629055023,0.948251485824585,0.0), (-0.45057186484336853,0.9716424942016602,0.0), (-0.44585955142974854,0.9869105219841003,0.0)]
wireBreakShape2 = [(-0.9789080023765564,0.9936655759811401,0.0), (-0.8673983812332153,0.993278443813324,0.0), (-0.7558938264846802,0.9922080636024475,0.0), (-0.644393265247345,0.9905911087989807,0.0), (-0.5328956842422485,0.9885642528533936,0.0), (-0.42140012979507446,0.9862641096115112,0.0), (-0.3099055886268616,0.9838272929191589,0.0), (-0.19841104745864868,0.9813904762268066,0.0), (-0.08691549301147461,0.9790903329849243,0.0), (0.024582073092460632,0.9770634770393372,0.0), (0.13608264923095703,0.9754465222358704,0.0), (0.24758723378181458,0.9743761420249939,0.0), (0.35909682512283325,0.973988950252533,0.0), (0.3707354664802551,0.9743118286132812,0.0), (0.386391282081604,0.9751754999160767,0.0), (0.4052528142929077,0.9764224290847778,0.0), (0.4265086352825165,0.977895200252533,0.0), (0.44934728741645813,0.9794362783432007,0.0), (0.4729573726654053,0.9808881878852844,0.0), (0.49652743339538574,0.9820934534072876,0.0), (0.5192460417747498,0.9828945994377136,0.0), (0.5403017401695251,0.9831340909004211,0.0), (0.5588830709457397,0.9826545119285583,0.0), (0.5741786360740662,0.9812983274459839,0.0), (0.585377037525177,0.9789080619812012,0.0), (0.6341516971588135,0.9542242884635925,0.0), (0.6788462996482849,0.9155604839324951,0.0), (0.7196342945098877,0.8651254177093506,0.0), (0.756689190864563,0.8051279187202454,0.0), (0.790184497833252,0.7377767562866211,0.0), (0.820293664932251,0.6652807593345642,0.0), (0.8471902012825012,0.5898487567901611,0.0), (0.8710475564002991,0.5136895179748535,0.0), (0.8920392394065857,0.4390118718147278,0.0), (0.9103387594223022,0.36802464723587036,0.0), (0.9261195659637451,0.3029366135597229,0.0), (0.9395551681518555,0.24595685303211212,0.0), (0.955365777015686,0.15229536592960358,0.0), (0.9596006274223328,0.05817600339651108,0.0), (0.9535955190658569,-0.036230720579624176,0.0), (0.9386863112449646,-0.130754292011261,0.0), (0.916208803653717,-0.22522418200969696,0.0), (0.8874987959861755,-0.3194698691368103,0.0), (0.8538922071456909,-0.4133208692073822,0.0), (0.8167248368263245,-0.5066066384315491,0.0), (0.7773324847221375,-0.5991566777229309,0.0), (0.7370510101318359,-0.6908004283905029,0.0), (0.6972162127494812,-0.7813674211502075,0.0), (0.6591639518737793,-0.8706870079040527,0.0), (0.6537741422653198,-0.8813779950141907,0.0), (0.6458905339241028,-0.893876850605011,0.0), (0.6359962224960327,-0.9076617956161499,0.0), (0.6245744228363037,-0.9222109913825989,0.0), (0.6121082305908203,-0.9370027184486389,0.0), (0.5990808010101318,-0.9515151381492615,0.0), (0.5859752893447876,-0.9652264714241028,0.0), (0.5732747912406921,-0.9776148796081543,0.0), (0.5614624619483948,-0.988158643245697,0.0), (0.5510214567184448,-0.9963359236717224,0.0), (0.5424349308013916,-1.0016249418258667,0.0), (0.5361859202384949,-1.0035037994384766,0.0), (0.4778144359588623,-1.003098487854004,0.0), (0.39090627431869507,-1.0019928216934204,0.0), (0.28116917610168457,-1.0003517866134644,0.0), (0.15431095659732819,-0.9983406662940979,0.0), (0.016039401292800903,-0.9961245656013489,0.0), (-0.1279377043247223,-0.9938686490058899,0.0), (-0.2719125747680664,-0.9917380809783936,0.0), (-0.41017740964889526,-0.9898980259895325,0.0), (-0.5370244383811951,-0.9885136485099792,0.0), (-0.6467458605766296,-0.9877501130104065,0.0), (-0.7336338758468628,-0.9877725839614868,0.0), (-0.7919809222221375,-0.9887463450431824,0.0), (-0.8472321033477783,-0.9877503514289856,0.0), (-0.8907361030578613,-0.9807220101356506,0.0), (-0.9230481386184692,-0.968161404132843,0.0), (-0.94472336769104,-0.9505686163902283,0.0), (-0.9563169479370117,-0.9284437894821167,0.0), (-0.9583840370178223,-0.902286946773529,0.0), (-0.9514797925949097,-0.8725982308387756,0.0), (-0.9361593723297119,-0.839877724647522,0.0), (-0.912977933883667,-0.8046254515647888,0.0), (-0.8824906945228577,-0.7673415541648865,0.0), (-0.8452528119087219,-0.7285261154174805,0.0), (-0.8018192052841187,-0.688679039478302,0.0), (-0.7605950236320496,-0.6552526354789734,0.0), (-0.7173190116882324,-0.6239956617355347,0.0), (-0.672552227973938,-0.5943365693092346,0.0), (-0.6268557906150818,-0.5657036304473877,0.0), (-0.5807907581329346,-0.5375252366065979,0.0), (-0.5349183082580566,-0.5092297792434692,0.0), (-0.48979946970939636,-0.48024559020996094,0.0), (-0.44599536061286926,-0.4500010311603546,0.0), (-0.40406709909439087,-0.4179244637489319,0.0), (-0.36457574367523193,-0.38344424962997437,0.0), (-0.328082412481308,-0.34598875045776367,0.0), (-0.29514816403388977,-0.3049863874912262,0.0), (-0.27178528904914856,-0.26538437604904175,0.0), (-0.25187304615974426,-0.21730707585811615,0.0), (-0.23535992205142975,-0.1623491793870926,0.0), (-0.2221943736076355,-0.10210538655519485,0.0), (-0.21232487261295319,-0.03817039728164673,0.0), (-0.2056998908519745,0.027861088514328003,0.0), (-0.20226791501045227,0.09439437836408615,0.0), (-0.20197740197181702,0.15983477234840393,0.0), (-0.2047768235206604,0.22258757054805756,0.0), (-0.2106146663427353,0.28105807304382324,0.0), (-0.21943938732147217,0.3336515724658966,0.0), (-0.2311994731426239,0.37877345085144043,0.0), (-0.24250823259353638,0.4108142852783203,0.0), (-0.2556721270084381,0.44234317541122437,0.0), (-0.2706804871559143,0.47274982929229736,0.0), (-0.2875226140022278,0.5014240145683289,0.0), (-0.30618783831596375,0.5277554392814636,0.0), (-0.3266654908657074,0.5511338114738464,0.0), (-0.34894490242004395,0.5709488987922668,0.0), (-0.3730153739452362,0.5865904092788696,0.0), (-0.3988662362098694,0.5974481105804443,0.0), (-0.4264868199825287,0.6029117107391357,0.0), (-0.4558664560317993,0.6023709177970886,0.0), (-0.48699450492858887,0.5952154994010925,0.0), (-0.495551198720932,0.5938780307769775,0.0), (-0.5040377378463745,0.5953200459480286,0.0), (-0.5124332904815674,0.5991383790969849,0.0), (-0.5207169651985168,0.6049299240112305,0.0), (-0.5288679599761963,0.6122915744781494,0.0), (-0.5368653535842896,0.620820164680481,0.0), (-0.5446884036064148,0.6301125288009644,0.0), (-0.5523161888122559,0.6397655606269836,0.0), (-0.5597279071807861,0.6493760943412781,0.0), (-0.5669026970863342,0.6585410237312317,0.0), (-0.5738196969032288,0.6668572425842285,0.0), (-0.5804580450057983,0.673921525478363,0.0), (-0.6044849753379822,0.6955807209014893,0.0), (-0.6346886157989502,0.7200635671615601,0.0), (-0.669962465763092,0.7465490102767944,0.0), (-0.7092000842094421,0.7742159366607666,0.0), (-0.7512949705123901,0.8022432327270508,0.0), (-0.7951406240463257,0.829809844493866,0.0), (-0.8396306037902832,0.8560947179794312,0.0), (-0.8836584091186523,0.8802767395973206,0.0), (-0.9261175394058228,0.9015348553657532,0.0), (-0.9659015536308289,0.919048011302948,0.0), (-1.001904010772705,0.9319950938224792,0.0), (-1.0330183506011963,0.9395549893379211,0.0), (-1.029815673828125,0.9406196475028992,0.0), (-1.0259003639221191,0.9435631632804871,0.0), (-1.021414875984192,0.948009729385376,0.0), (-1.0165019035339355,0.9535835981369019,0.0), (-1.0113037824630737,0.9599090218544006,0.0), (-1.0059632062911987,0.9666101932525635,0.0), (-1.0006226301193237,0.9733113646507263,0.0), (-0.9954245686531067,0.9796367883682251,0.0), (-0.9905115365982056,0.985210657119751,0.0), (-0.9860261082649231,0.9896572232246399,0.0), (-0.9821107983589172,0.9926007390022278,0.0)]
wireBreakShape3 = [(0.5300589799880981,-1.0012426376342773,0.0), (0.6678270101547241,-0.9809858202934265,0.0), (0.7298487424850464,-0.9508764147758484,0.0), (0.7736494541168213,-0.915550947189331,0.0), (0.8132549524307251,-0.8903615474700928,0.0), (0.8391478657722473,-0.8603184223175049,0.0), (0.8541088104248047,-0.8257798552513123,0.0), (0.8596541881561279,-0.7874497175216675,0.0), (0.8566010594367981,-0.7462944388389587,0.0), (0.8455622792243958,-0.7034978866577148,0.0), (0.8271644115447998,-0.6603543758392334,0.0), (0.8019912838935852,-0.6180073022842407,0.0), (0.7703878879547119,-0.5770812034606934,0.0), (0.7323455810546875,-0.5374261140823364,0.0), (0.6876468658447266,-0.49820294976234436,0.0), (0.6362594366073608,-0.458327054977417,0.0), (0.5787626504898071,-0.4170251488685608,0.0), (0.5165627598762512,-0.37419795989990234,0.0), (0.4546539783477783,-0.2678256332874298,0.0), (0.3984636068344116,-0.15310174226760864,0.0), (0.33635756373405457,-0.111056387424469,0.0), (0.279043972492218,-0.07182556390762329,0.0), (0.23466166853904724,0.028352461755275726,0.0), (0.18970444798469543,0.05873250216245651,0.0), (0.15002770721912384,0.08347398042678833,0.0), (0.11389237642288208,0.10198787599802017,0.0), (0.0793885737657547,0.11386007815599442,0.0), (0.04497428610920906,0.11893228441476822,0.0), (0.009747032076120377,0.11739175766706467,0.0), (-0.026577983051538467,0.10979871451854706,0.0), (-0.06385840475559235,0.0970257967710495,0.0), (-0.10174186527729034,0.08013788610696793,0.0), (-0.13984671235084534,0.06025131791830063,0.0), (-0.17791970074176788,0.03838548809289932,0.0), (-0.22282546758651733,-0.049599677324295044,0.0), (-0.2613450288772583,-0.07352438569068909,0.0), (-0.3011779189109802,-0.09838157892227173,0.0), (-0.3434284031391144,-0.12463068962097168,0.0), (-0.38907960057258606,-0.1528727114200592,0.0), (-0.4471473693847656,-0.22057607769966125,0.0), (-0.5572159290313721,-0.3221653401851654,0.0), (-0.6129419207572937,-0.3577440083026886,0.0), (-0.6697011590003967,-0.3951415717601776,0.0), (-0.7968481779098511,-0.47950056195259094,0.0), (-0.8502304553985596,-0.5198425650596619,0.0), (-0.8992668390274048,-0.5627232789993286,0.0), (-0.9420168399810791,-0.6099779009819031,0.0), (-0.9757494926452637,-0.6634405851364136,0.0), (-0.9963312149047852,-0.7235201597213745,0.0), (-0.9981893301010132,-0.7880244851112366,0.0), (-0.9752516746520996,-0.8522047400474548,0.0), (-0.9225941896438599,-0.9102230072021484,0.0), (-0.803798258304596,-0.9856590628623962,0.0), (-0.6051443815231323,-1.0055497884750366,0.0), (-0.4569494426250458,-1.0071760416030884,0.0), (-0.2938075363636017,-1.008771538734436,0.0), (-0.11784977465867996,-1.00869619846344,0.0), (0.06064537912607193,-1.0088180303573608,0.0), (0.23858767747879028,-1.0081573724746704,0.0), (0.40061578154563904,-1.0058997869491577,0.0)]

#Main for loop
for pictureNumber in range(numOfPictures):
    #Point coordinates array
    wirePoints = []
 
    #Hole position errors
    holePositionErrors = []
	
	#Rotate camera
    rotate = pictureNumber % 4
    bpy.data.objects['Camera'].rotation_euler[2] = rotate * 1.5708
    
	#Number of wires and hole cloggings
    numOfWires = random.randint(1, maxWires)
	
    #Delete everything
    deleteEverything()
                
    #Modify sizes in every run
    scaleSizes()
         
    #At first call delete default elements, create materials, and set camera and lights
    if (pictureNumber == 0):
        createMaterials()
        setLight()
        setCamera()
    
    #Create annoation file
    outF = open(path+"Dataset\\"+"model"+str(pictureNumber)+'.txt', "w")
    
    #Generate coordinates of the points
    pointGenerator()
    
    #Calculate hole position errors
    calculateHolePositionErrors()
    
    #Create surface
    createSurface()
    
    #Create wires
    createWires()
    
    #Add wire breaks
    addWireBreaks()
    
    #Create soldering surfaces
    createSolderingSurfaces()
    
    #Create holes
    createHoles()
    
    #Add hole cloggings
    addHoleCloggings()
    
    #Close annoation file
    outF.close()
    
    #Render model
    renderModel()
