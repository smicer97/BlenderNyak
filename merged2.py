import bpy, bmesh, os, random
from collections import defaultdict
from math import atan, pi, radians
import math


def getFuratEltomodesPos():
    valtozo = 0
    volt_mar_ilyen = 0
    while valtozo < num_of_FuratEltomodes:
        NumTemp = random.randint(0, len(x)-1)
        for elem in PosTemp:
            if (NumTemp == elem):
                volt_mar_ilyen = 1
                break
        if (volt_mar_ilyen):
            valtozo = valtozo
            volt_mar_ilyen = 0
        else:
            PosTemp.append(NumTemp)
            valtozo = valtozo + 1

def transformXY(x,y):
    transformedX = x*math.cos(-rotate*1.5708)-y*math.sin(-rotate*1.5708)
    transformedY = x*math.sin(-rotate*1.5708)+y*math.cos(-rotate*1.5708)
    return transformedX,transformedY

def writeObjectCoordinateToTxt(X,Y,surfaceSize,imageMax,objectSize,classId):
    X,Y = transformXY(X,Y)
    scaleFactor = imageMax / surfaceSize
    offset = imageMax / 2
    x = int(scaleFactor * X + offset)
    y = int(-scaleFactor * Y + offset)    
    if (x > imageMax):
        x = imageMax        
    if (y > imageMax):
        y = imageMax
    x_center = x/imageMax
    y_center = y/imageMax
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

#Calculate y from x
def calculate_y(x1, y1, x2, y2, x):
    y = y1+(y2-y1)*(x-x1)/(x2-x1)
    return y

#Calculate x from y
def calculate_x(x1, y1, x2, y2, y):
    x = x1+(x2-x1)*(y-y1)/(y2-y1)
    return x

#Direction of the "szakadás"
def calculateDirection(x1, y1, x2, y2):
    if (x1 == x2):
        k = random.randint(0, 1)
        return 90 + k*180
    else:
        direction = atan((y1-y2)/(x1-x2)) * 180 / pi
        k = random.randint(0, 1)
        if (direction < 0):
            return direction + 180 + k*180
        else:
            return direction + k*180

#X and Y generation for "szakadás coordinate"
def generateXY(x1,y1,x2,y2):
    if (abs(x1 - x2) > abs(y1 - y2)):
        #Generate x coordinate of szakadás
        x = random.uniform(x1, x2)      
        #Calculate y coordinate from x 
        y = calculate_y(x1, y1, x2, y2, x)
    else:
        #Generate y coordinate of szakadás
        y = random.uniform(y1, y2)      
        #Calculate x coordinate from y 
        x = calculate_x(x1, y1, x2, y2, y)        
    return x,y        

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

def createShape(pointsShape):
    #Create object for line
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
    
def addRandomSzakadas(points, width, forrszemRadius):
    #50% chance of szakadás
    k = random.randint(0, 1)
    if (k == 1):
        pointsShape = [(-0.44056040048599243,0.9923735857009888,0.0), (-0.37828749418258667,0.9923735857009888,0.0), (-0.284443736076355,0.9923735857009888,0.0), (-0.1653432846069336,0.9923735857009888,0.0), (-0.027300313115119934,0.9923735857009888,0.0), (0.12337100505828857,0.9923735857009888,0.0), (0.2803564965724945,0.9923735857009888,0.0), (0.43734198808670044,0.9923735857009888,0.0), (0.5880132913589478,0.9923735857009888,0.0), (0.7260562777519226,0.9923735857009888,0.0), (0.845156729221344,0.9923735857009888,0.0), (0.9390004873275757,0.9923735857009888,0.0), (1.0012736320495605,0.9923735857009888,0.0), (0.9885700941085815,0.9593090415000916,0.0), (0.962232232093811,0.9055152535438538,0.0), (0.9248384237289429,0.8352116942405701,0.0), (0.8789671063423157,0.7526178359985352,0.0), (0.8271965980529785,0.6619531512260437,0.0), (0.77210533618927,0.5674371123313904,0.0), (0.7162717580795288,0.47328925132751465,0.0), (0.662274181842804,0.3837289810180664,0.0), (0.6126910448074341,0.3029758036136627,0.0), (0.570100724697113,0.23524919152259827,0.0), (0.5370815992355347,0.18476863205432892,0.0), (0.5162120461463928,0.15575364232063293,0.0), (0.4614240527153015,0.09101337194442749,0.0), (0.40359848737716675,0.026070058345794678,0.0), (0.34289294481277466,-0.038498036563396454,0.0), (0.2794649600982666,-0.10211264342069626,0.0), (0.2134721279144287,-0.1641954928636551,0.0), (0.14507202804088593,-0.2241683304309845,0.0), (0.07442222535610199,-0.28145289421081543,0.0), (0.0016802921891212463,-0.33547088503837585,0.0), (-0.07299619168043137,-0.3856440484523773,0.0), (-0.1494496464729309,-0.43139412999153137,0.0), (-0.22752252221107483,-0.47214287519454956,0.0), (-0.3070572018623352,-0.5073120594024658,0.0), (-0.35896116495132446,-0.5280007719993591,0.0), (-0.40206748247146606,-0.5448148250579834,0.0), (-0.4377216100692749,-0.5581926703453064,0.0), (-0.46726903319358826,-0.5685728192329407,0.0), (-0.4920552372932434,-0.576393723487854,0.0), (-0.5134257078170776,-0.5820938944816589,0.0), (-0.5327259302139282,-0.5861117839813232,0.0), (-0.5513014197349548,-0.5888859033584595,0.0), (-0.5704975724220276,-0.5908547043800354,0.0), (-0.5916599631309509,-0.5924566984176636,0.0), (-0.6161340475082397,-0.5941303968429565,0.0), (-0.6452652215957642,-0.5963141918182373,0.0), (-0.6426652669906616,-0.5318052172660828,0.0), (-0.6353951096534729,-0.4457327425479889,0.0), (-0.6242491602897644,-0.34242069721221924,0.0), (-0.6100218892097473,-0.22619304060935974,0.0), (-0.5935077667236328,-0.10137371718883514,0.0), (-0.5755012035369873,0.027713298797607422,0.0), (-0.5567967295646667,0.1567440629005432,0.0), (-0.5381887555122375,0.2813946008682251,0.0), (-0.5204718112945557,0.39734095335006714,0.0), (-0.5044403076171875,0.5002591609954834,0.0), (-0.49088868498802185,0.5858253240585327,0.0), (-0.4806113839149475,0.6497154235839844,0.0), (-0.4779691994190216,0.6705268025398254,0.0), (-0.47543078660964966,0.6983524560928345,0.0), (-0.4729270935058594,0.7315105199813843,0.0), (-0.47038906812667847,0.7683190703392029,0.0), (-0.46774762868881226,0.8070961236953735,0.0), (-0.46493369340896606,0.846159815788269,0.0), (-0.4618782103061676,0.8838282227516174,0.0), (-0.4585121273994446,0.9184194207191467,0.0), (-0.4547663629055023,0.948251485824585,0.0), (-0.45057186484336853,0.9716424942016602,0.0), (-0.44585955142974854,0.9869105219841003,0.0)]
        createShape(pointsShape)
        
        #Chose 2 points to generate szakadás
        i = random.randint(0, len(points)-2)
        
        #Calculate degree
        degrees = calculateDirection(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        radians = math.radians(degrees)
        bpy.context.object.rotation_euler[2] = radians
        
        #Set size
        bpy.context.object.scale[0] = width
        bpy.context.object.scale[1] = width

        #Set coordinate
        #If szakadás is next to the furat, y0 has to be greater
        if (i ==0):
            x,y = generateXY(points[i][0],points[i][1] + forrszemRadius + width/2,points[i+1][0],points[i+1][1])
        else:
            x,y = generateXY(points[i][0],points[i][1],points[i+1][0],points[i+1][1])
            
        bpy.context.object.location[0] = x
        bpy.context.object.location[1] = y
        
        #Write to .txt
        writeObjectCoordinateToTxt(x,y,size,imageMaxSize,width,0)
        
def addSzakadas(points, width, forrszemRadius):
    #50% chance of szakadás
    k = random.randint(0, 1)
    if (k == 1):
        #Chose 2 points to generate szakadás
        i = random.randint(0, len(points)-2)
        #Create object for szakadás
        bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(15, 0, 0.02), scale=(1, 1, 1))
        bpy.context.object.name = "Szakadas"
        bpy.context.object.scale[1] = width
        bpy.context.object.scale[0] = width
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        #Calculate degree
        degrees = calculateDirection(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        radians = math.radians(degrees)
        bpy.context.object.rotation_euler[2] = radians
        
        #Assign material
        assignMaterial("Surface", bpy.context.object)
        
        #Set coordinate
        #If szakadás is next to the furat, y0 has to be greater
        if (i ==0):
            x,y = generateXY(points[i][0],points[i][1] + forrszemRadius + width/2,points[i+1][0],points[i+1][1])
        else:
            x,y = generateXY(points[i][0],points[i][1],points[i+1][0],points[i+1][1])
            
        bpy.context.object.location[0] = x
        bpy.context.object.location[1] = y
        
        #Write to .txt
        writeObjectCoordinateToTxt(x,y,size,imageMaxSize,width,0)
        
def assignMaterial(color, obj):
    mat = bpy.data.materials.get(color)
    obj.active_material = mat
        
def createMaterials():
    #Create green material
    materialHole = bpy.data.materials.new("Hole")
    materialHole.diffuse_color = (0,0,0,1)
    
    #Create gray material
    materialEltomodes = bpy.data.materials.new("Eltomodes")
    materialEltomodes.diffuse_color = (0.8,0.8,0.8,1)
    
    #Create image material
    mat = bpy.data.materials.new(name="Surface")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load("C:\\Users\\Roland\\Desktop\\BME mechatronika MSc\\Első félév - 2020-2021-2 (tavasz)\\Projektfeladat\\surface.png")
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    
    #Create image material
    mat = bpy.data.materials.new(name="Line")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load("C:\\Users\\Roland\\Desktop\\BME mechatronika MSc\\Első félév - 2020-2021-2 (tavasz)\\Projektfeladat\\line.png")
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])  

def camera():
    #Modify camera postiton
    objCamera = bpy.data.objects.get("Camera")
    objCamera.rotation_euler[0] = 0
    objCamera.rotation_euler[1] = 0
    objCamera.rotation_euler[2] = 0
    objCamera.location[0] = 0
    objCamera.location[1] = 0
    objCamera.location[2] = 27.778

def light():
    #Add light
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

def surface():
    #Add surface
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, -0.001), scale=(1, 1, 1))
    bpy.context.object.name = "Surface"
    bpy.context.object.scale[1] = 10
    bpy.context.object.scale[0] = 10
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    objSurface = bpy.data.objects.get("Surface")
    
    #Assign material
    assignMaterial("Surface", objSurface)
    
def templatePlane(width):
    #Create the template plane objct
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(15, 0, 0), scale=(1, 1, 1))
    bpy.context.object.name = "TemplatePlane"
    bpy.context.object.scale[1] = 0.001
    #Width of the line
    bpy.context.object.scale[0] = width
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.convert(target='CURVE')
    
def createLineBetweenPoints(points):
    #Create object for line
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
    assignMaterial("Line", objLine)

def render(imageMax):
    #Render
    imagePath = "C:\\Users\\Roland\\Desktop\\BME mechatronika MSc\\Első félév - 2020-2021-2 (tavasz)\\Projektfeladat\\"
    #bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    if os.path.exists(imagePath):
        bpy.context.scene.render.filepath = imagePath+'model'+str(PictureNumber)+'.jpg'
        bpy.context.scene.render.resolution_x = imageMax
        bpy.context.scene.render.resolution_y = imageMax
        bpy.ops.render.render(write_still=True)
    else:
        print("Wrong path")   

def createForrszem(forrszemRadius):
    #Create the Forrszem object (nem csak egy, hanem az összes forrszem generálása)
    for j in range (len(x)):
        bpy.ops.mesh.primitive_cylinder_add(radius=forrszemRadius, depth=0.001, enter_editmode=False, align='WORLD', location=(x[j], y[j], 0.0015), scale=(1, 1, 1))
        bpy.context.object.name = "Forrszem"+str(j)
        bpy.context.object.scale[1] = 1
        bpy.context.object.scale[0] = 1

    Forrszem_array = ["Forrszem0"]

    for k in range(1, len(x)):
        Forrszem_array.append("Forrszem"+str(k))
        
    bpy.ops.object.select_all(action='DESELECT')

    for o in bpy.data.objects:
        if o.name in Forrszem_array:
            o.select_set(True)

    bpy.ops.object.join()
    bpy.context.object.name = "Forrszem"
    objForrszem = bpy.data.objects.get("Forrszem")
    assignMaterial("Line", objForrszem)

def createHoles(holeRadius):
    #Create holes object
    for l in range (len(x)):
        bpy.ops.mesh.primitive_cylinder_add(radius=holeRadius, depth=0.001, enter_editmode=False, align='WORLD', location=(x[l] + x_error, y[l] + y_error, 0.0025), scale=(1, 1, 1))
        bpy.context.object.name = "Holes"+str(l)
        bpy.context.object.scale[1] = 1
        bpy.context.object.scale[0] = 1

    Holes_array = ["Holes0"]

    for m in range(1, len(x)):
        Holes_array.append("Holes"+str(m))
        
    bpy.ops.object.select_all(action='DESELECT')

    for p in bpy.data.objects:
        if p.name in Holes_array:
            p.select_set(True)

    bpy.ops.object.join()
    bpy.context.object.name = "Holes"
    objHoles = bpy.data.objects.get("Holes")
    assignMaterial("Hole", objHoles)

def createFuratEltomodes(holeRadius):
    #furat eltömődés létrehozása
    if(num_of_FuratEltomodes != 0):
        #num_of_FuratEltomodes értéknek megfelelő számú furat random kiválasztása, ahova a furat eltömődést tesszük
        getFuratEltomodesPos()
        #create FuratEltomodes object
        for l in range (num_of_FuratEltomodes):
            bpy.ops.mesh.primitive_cylinder_add(radius=holeRadius, depth=0.001, enter_editmode=False, align='WORLD', location=(x_error + x[PosTemp[l]], y_error + y[PosTemp[l]], 0.0035), scale=(1, 1, 1))
            bpy.context.object.name = "FuratEltomodes"+str(l)
            bpy.context.object.scale[1] = 1
            bpy.context.object.scale[0] = 1

        FuratEltomodes_array = ["FuratEltomodes0"]
        for m in range(1, len(x)):
            FuratEltomodes_array.append("FuratEltomodes"+str(m))
            
        bpy.ops.object.select_all(action='DESELECT')
        for p in bpy.data.objects:
            if p.name in FuratEltomodes_array:
                p.select_set(True)

        bpy.ops.object.join()
        bpy.context.object.name = "FuratEltomodes"
        objFuratEltomodes = bpy.data.objects.get("FuratEltomodes")
        
        if(num_of_FuratEltomodes != 0):
            assignMaterial("Eltomodes", objFuratEltomodes)

def deleteCube():
    for o in bpy.context.scene.objects:
        if o.name == "Cube":
            bpy.ops.object.delete()
            
def deleteEverything():
    ob1 = bpy.context.scene.objects["Camera"]
    ob2 = bpy.context.scene.objects["Light"]       
    bpy.ops.object.select_all(action='SELECT') 
    bpy.context.view_layer.objects.active = ob1   
    ob1.select_set(False)
    bpy.context.view_layer.objects.active = ob2   
    ob2.select_set(False)

    bpy.ops.object.delete(use_global=False, confirm=False)

def pointGenerator():
    global numOfLines
    numOfLines = random.randint(1, maxLines)

    #Determine the difference of the points according to num of lines
    pointDiff = size / (2 * numOfLines)
    
    for i in range(numOfLines):
        # x0 can be the following, if size is 20
        # 3 lines: -6.66, 0, 6.66
        # 2 lines: -5, 5
        # 1 lines: 0 
        #Scale i to 1,3,5
        scaleFactor = (i * 2 + 1) 
        maxSpace = pointDiff - width
        
        #5 is a magic number
        y0Max = size - 1 - maxSpace - forrszemRadius - 5 * width
        y1Max = size - 1 - maxSpace
        
        x0 = pointDiff * scaleFactor - size/2
        y0 = random.uniform(1, y0Max) -	size/2
            
        x1 = x0
        y1 = random.uniform(y0 + forrszemRadius + width + size/2, y1Max) - size/2
        
        #Branch direction
        # -1 left, 0 straight, 1 right
        direction = random.randint(-1, 1)
        
        if (direction == 0):
            x2 = x1
            y2 = size/2
            #Put into points array
            points = [(x0, y0, 0.0), (x1, y1, 0.0), (x2, y2, 0.0)]
        else:
            maxBranch = maxSpace * math.sqrt(2)
            #Generate length of branch
            branchLength = random.uniform(math.sqrt(2), maxBranch)
            x2 = x1 + direction * branchLength / math.sqrt(2)
            y2 = y1 + branchLength / math.sqrt(2)  
                  
            x3 = x2
            y3 = size/2
            #Put into points array
            points = [(x0, y0, 0.0), (x1, y1, 0.0), (x2, y2, 0.0), (x3, y3, 0.0)]
        
        #Create lines
        createLineBetweenPoints(points)
        
        #Decide which "szakadás" will be added
        szakadas = random.randint(0, 1)
        if(szakadas==0):
            addRandomSzakadas(points, width, forrszemRadius)
        else:
            addSzakadas(points, width, forrszemRadius)
        
        #points tömbből a furat középpontok kinyerése
        x.append(x0)
        y.append(y0)
    
#BEMENETI PARAMÉTER:
#renderelni kívánt képek darabszáma
num_of_pictures = 10

#BEMENETI PARAMÉTEREK:
#pointGenerator-höz kezdeti változók
maxLines = 6
#Surface size
size = 2 * 10
#Line and szakadás vastagság
width = 0.2
forrszemRadius = 0.75
holeRadius = 0.5
#Size modifier
sizeScale = 1

imageMaxSize = 1080

#Main for loop
for PictureNumber in range(num_of_pictures):
    
    #furat-forrszem pozíció hibához az x és y irányú középpont eltérés (egy kicsit ki tud menni a forrszemből a furat) (egy képen mindegyik ugyanúgy tér el, de képenként más)
    x_error = random.uniform(0, forrszemRadius-holeRadius)
    y_error = random.uniform(0, forrszemRadius-holeRadius)
    
    #num_of_FuratEltomodes értéknek megfelelő számú furat random kiválasztása, ahova a furat eltömődést tesszük
    PosTemp = []
    NumTemp = 0
    
    #furat középpontokhoz inicializálás
    x = []
    y = []
    
    #Modify size in every run
    width /= sizeScale
    forrszemRadius /= sizeScale
    holeRadius /= sizeScale
    sizeScale = random.uniform(1, 1.4)
    width *= sizeScale
    forrszemRadius *= sizeScale
    holeRadius *= sizeScale
                
    if (PictureNumber == 0):
        deleteCube()
        createMaterials()
        light()
        camera()
    surface()
    templatePlane(width)
    
    #Rotate camera
    rotate = PictureNumber % 4
    bpy.data.objects['Camera'].rotation_euler[2] = rotate * 1.5708
    
    #Create annoation file
    outF = open("C:\\Users\\Gergő\\Desktop\\BME\\Msc\\3. félév\\Diploma\\Dataset\\"+"model"+str(PictureNumber)+'.txt', "w")
    
    pointGenerator()    
    
    createForrszem(forrszemRadius)
    createHoles(holeRadius)
    
    #furat eltömődések számának generálása
    num_of_FuratEltomodes = random.randint(0, numOfLines)
    
    createFuratEltomodes(holeRadius)
    
    #Write "furat eltömődés" error to txt
    for index in PosTemp:
        writeObjectCoordinateToTxt(x[index],y[index],size,imageMaxSize,forrszemRadius,1)
    
    #Close annoation file
    outF.close()
    
    render(imageMaxSize)
    
    deleteEverything()
