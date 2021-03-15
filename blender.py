import bpy, bmesh, os, random

def calculate_y(x1, y1, x2, y2, x):
    y = y1+(y2-y1)*(x-x1)/(x2-x1)
    return y
def startup():
    global objLine
    global objSurface
    global materialGreen
    global materialGray
    global objSzakadas
    #Create green material
    materialGreen = bpy.data.materials.new("Green")
    materialGreen.diffuse_color = (0,1,0,1)
    #Create gray material
    materialGray = bpy.data.materials.new("Gray")
    materialGray.diffuse_color = (0.8,0.8,0.8,1)
    
    #Add light
    bpy.data.objects['Light'].select_set(True)
    bpy.ops.object.delete() 
    bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, 0, 50), scale=(1, 1, 1))
    
    #Add surface
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, -0.01), scale=(1, 1, 1))
    bpy.context.object.name = "Surface"
    bpy.context.object.scale[1] = 10
    bpy.context.object.scale[0] = 10
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    objSurface = bpy.data.objects.get("Surface")

    #Create the template plane objct
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(15, 0, 0), scale=(1, 1, 1))
    bpy.context.object.name = "TemplatePlane"
    bpy.context.object.scale[1] = 0.001
    bpy.context.object.scale[0] = 0.1
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.convert(target='CURVE')

    #Create camera
    objCamera = bpy.data.objects.get("Camera")
    objCamera.rotation_euler[0] = 0
    objCamera.rotation_euler[1] = 0
    objCamera.rotation_euler[2] = 0
    objCamera.location[0] = 0
    objCamera.location[1] = 0
    objCamera.location[2] = 25

    #Create object for line
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.context.object.name = "Line"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    objLine = bpy.data.objects.get("Line")

startup()

bm = bmesh.from_edit_mesh(objLine.data)

#Dots
points = [(0.0, 0.0, 0.0), (0.0, 5.0, 0.0), (5.0, 5.0, 0.0), (5.0, 0.0, 0.0)]

v1 = bm.verts.new(points[0])
v2 = bm.verts.new(points[1])
v3 = bm.verts.new(points[2])
v4 = bm.verts.new(points[3])

#for i in range(3):
#    v.append(bm.verts.new(points[i+1]))


v = [v1, v2, v3, v4] 

for i in range(len(v)-1):
    bm.edges.new((v[i], v[i+1]))

bmesh.update_edit_mesh(objLine.data)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.convert(target='CURVE')

#Apply the template on line object
objLine.data.bevel_mode = 'OBJECT'
objLine.data.bevel_object = bpy.data.objects["TemplatePlane"]

#Assign material
objLine.active_material = materialGray
objSurface.active_material = materialGreen

#Add "szakadas"
#k = random.randint(0, 1)
k = 1
if (k == 1):
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(15, 0, 0.02), scale=(1, 1, 1))
    bpy.context.object.name = "Szakadas"
    bpy.context.object.scale[1] = 0.2
    bpy.context.object.scale[0] = 0.2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    objSzakadas= bpy.data.objects.get("Szakadas")
    objSzakadas.active_material = materialGreen
    if(points[2][0] > points[1][0]):
        x = random.randint(points[1][0], points[2][0])
    else:
        x = random.randint(points[2][0], points[1][0])
    print(x)
    y = calculate_y(points[1][0], points[1][1], points[2][0], points[2][1], x)
    print(x)
    print(y)
    bpy.context.object.location[0] = x
    bpy.context.object.location[1] = y

    
#Render
imagePath = "C:\\Users\\Gergő\\Desktop\\BME\\Msc\\3. félév\\Diploma\\"

if os.path.exists(imagePath):
    bpy.context.scene.render.filepath = imagePath+'model.jpg'
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080
    bpy.ops.render.render(write_still=True)
else:
    print("Wrong path")