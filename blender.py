import bpy, bmesh, os, random
from collections import defaultdict

def calculate_y(x1, y1, x2, y2, x):
    y = y1+(y2-y1)*(x-x1)/(x2-x1)
    return y

def calculate_x(x1, y1, x2, y2, y):
    x = x1+(x2-x1)*(y-y1)/(y2-y1)
    return x

def addSzakadas(points):
    #50% chance of szakadás
    k = random.randint(0, 1)
    if (k == 1):
        #Chose 2 points to generate szakadás
        i = random.randint(0, len(points)-2)
        #Create object for szakadás
        bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(15, 0, 0.02), scale=(1, 1, 1))
        bpy.context.object.name = "Szakadas"
        bpy.context.object.scale[1] = 0.2
        bpy.context.object.scale[0] = 0.2
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        #Assign material
        assignMaterial("Green", bpy.context.object)
        
        if (abs(points[i][0] - points[i+1][0]) > abs(points[i][1] - points[i+1][1])):
            #Generate x coordinate of szakadás
            x = random.uniform(points[i][0], points[i+1][0])      
            #Calculate y coordinate from x 
            y = calculate_y(points[i][0], points[i][1], points[i+1][0], points[i+1][1], x)
        else:
            #Generate y coordinate of szakadás
            y = random.uniform(points[i][1], points[i+1][1])      
            #Calculate x coordinate from y 
            x = calculate_x(points[i][0], points[i][1], points[i+1][0], points[i+1][1], y)

        bpy.context.object.location[0] = x
        bpy.context.object.location[1] = y

def assignMaterial(color, obj):
    mat = bpy.data.materials.get(color)
    obj.active_material = mat
        
def createMaterails():
    #Create green material
    materialGreen = bpy.data.materials.new("Green")
    materialGreen.diffuse_color = (0,1,0,1)
    #Create gray material
    materialGray = bpy.data.materials.new("Gray")
    materialGray.diffuse_color = (0.8,0.8,0.8,1)
    #Create image material
    mat = bpy.data.materials.new(name="Surface")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load("C:\\Users\\Gergő\\Desktop\\BME\\Msc\\3. félév\\Diploma\\BlenderNyak\\surface.jpg")
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    
    #Create image material
    mat = bpy.data.materials.new(name="Line")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load("C:\\Users\\Gergő\\Desktop\\BME\\Msc\\3. félév\\Diploma\\BlenderNyak\\line.jpg")
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    

def camera():
    #Modify camera postiton
    objCamera = bpy.data.objects.get("Camera")
    objCamera.rotation_euler[0] = 0
    objCamera.rotation_euler[1] = 0
    objCamera.rotation_euler[2] = 0
    objCamera.location[0] = 0
    objCamera.location[1] = 0
    objCamera.location[2] = 25

def light():
    #Delete default light
    bpy.data.objects['Light'].select_set(True)
    bpy.ops.object.delete() 
    #Add light
    bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, 0, 50), scale=(1, 1, 1))

def surface():
    global objSurface
    #Add surface
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, -0.01), scale=(1, 1, 1))
    bpy.context.object.name = "Surface"
    bpy.context.object.scale[1] = 10
    bpy.context.object.scale[0] = 10
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    objSurface = bpy.data.objects.get("Surface")
    
    #Assign material
    assignMaterial("Green", objSurface)
    
def templatePlane():
    #Create the template plane objct
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(15, 0, 0), scale=(1, 1, 1))
    bpy.context.object.name = "TemplatePlane"
    bpy.context.object.scale[1] = 0.001
    bpy.context.object.scale[0] = 0.1
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.convert(target='CURVE')
    
def createLineBetweenPoints(points):
    #Create object for line
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.context.object.name = "Line"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    objLine = bpy.data.objects.get("Line")
    
    bm = bmesh.from_edit_mesh(objLine.data)
    
    #Store verts into "v" list
    v = defaultdict(list)
    for i in range(len(points)):
        vtemp = bm.verts.new(points[i])
        v[""].append(vtemp)

    #Create edges from the the "v" list
    for i in range(len(v[""])-1):
        bm.edges.new((v[""][i], v[""][i+1]))    
         
    bmesh.update_edit_mesh(objLine.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.convert(target='CURVE')

    #Apply the template on line object
    objLine.data.bevel_mode = 'OBJECT'
    objLine.data.bevel_object = bpy.data.objects["TemplatePlane"]

    #Assign material
    assignMaterial("Gray", objLine)

def render():
    #Render
    imagePath = "C:\\Users\\Gergő\\Desktop\\BME\\Msc\\3. félév\\Diploma\\"

    if os.path.exists(imagePath):
        bpy.context.scene.render.filepath = imagePath+'model.jpg'
        bpy.context.scene.render.resolution_x = 1080
        bpy.context.scene.render.resolution_y = 1080
        bpy.ops.render.render(write_still=True)
    else:
        print("Wrong path")   
        
def startup():
    createMaterails()
    light()
    surface()
    templatePlane()
    camera()

#Comment this line after first run    
startup()

#Dots
points = [(0.0, 0.0, 0.0), (0.0, -5.0, 0.0), (-5.0, -5.0, 0.0), (-5.0, 0.0, 0.0)]

createLineBetweenPoints(points)

#Add "szakadas"
addSzakadas(points)

render()