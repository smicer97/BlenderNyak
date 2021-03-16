import bpy, bmesh

#furat középpontok megadása
# x1, x2, x3 ...
# y1, y2, y3 ...
x = [4, -1]
y = [1, -5]

#Create green material
materialGreen = bpy.data.materials.new("Green")
materialGreen.diffuse_color = (0,1,0,1)
#Create gray material
materialGray = bpy.data.materials.new("Gray")
materialGray.diffuse_color = (0.8,0.8,0.8,1)

#Create the Surface object
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, -0.01), scale=(1, 1, 1))
bpy.context.object.name = "Surface"
bpy.context.object.scale[1] = 10
bpy.context.object.scale[0] = 10
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
objSurface = bpy.data.objects.get("Surface")

#Create holes in the Surface object
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.delete(type='ONLY_FACE')
for i in range (len(x)):
    bpy.ops.mesh.primitive_circle_add(radius=1, enter_editmode=False, align='WORLD', location=(x[i], y[i], 0), scale=(1, 1, 1))
bpy.ops.object.mode_set(mode='EDIT')
bpy.context.tool_settings.mesh_select_mode = (False, True, False)
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.fill()
bpy.ops.object.mode_set(mode='OBJECT')

#Create the template plane object
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(100, 0, 0), scale=(1, 1, 1))
bpy.context.object.name = "TemplatePlane"
bpy.context.object.scale[1] = 0.001
bpy.context.object.scale[0] = 0.1
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.object.convert(target='CURVE')

#Create object for line
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
bpy.context.object.name = "Line"
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.delete(type='VERT')

objLine = bpy.data.objects.get("Line")
bm = bmesh.from_edit_mesh(objLine.data)

#Create Dots
d1 = bm.verts.new((x[0], y[0], 0.0))
d2 = bm.verts.new((x[0], y[0]+3, 0.0))
d3 = bm.verts.new((x[1], y[1], 0.0))
d4 = bm.verts.new((x[1], y[1]+3, 0.0))

bm.edges.new((d1, d2))
#bm.edges.new((d2, d3))
bm.edges.new((d3, d4))

bmesh.update_edit_mesh(objLine.data)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.convert(target='CURVE')

#Apply the template on line object
objLine.data.bevel_mode = 'OBJECT'
objLine.data.bevel_object = bpy.data.objects["TemplatePlane"]

#Create the Forrszem object (nem csak egy, hanem az összes forrszem generálása)
for j in range (len(x)):
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.01, enter_editmode=False, align='WORLD', location=(x[j], y[j], 0), scale=(1, 1, 1))
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

#Create lukasztó Cylinders object
for l in range (len(x)):
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=4, enter_editmode=False, align='WORLD', location=(x[l], y[l], 0), scale=(1, 1, 1))
    bpy.context.object.name = "LukasztoCylinder"+str(l)
    bpy.context.object.scale[1] = 1
    bpy.context.object.scale[0] = 1

LukasztoCylinder_array = ["LukasztoCylinder0"]

for m in range(1, len(x)):
    LukasztoCylinder_array.append("LukasztoCylinder"+str(m))
    
bpy.ops.object.select_all(action='DESELECT')

for p in bpy.data.objects:
    if p.name in LukasztoCylinder_array:
        p.select_set(True)

bpy.ops.object.join()
bpy.context.object.name = "LukasztoCylinder"
objLukasztoCylinder = bpy.data.objects.get("LukasztoCylinder")

#cutting holes into the Forrszem
    #Forrszem kijelölés
ob = bpy.context.scene.objects["Forrszem"]       
bpy.ops.object.select_all(action='DESELECT') 
bpy.context.view_layer.objects.active = ob   
ob.select_set(True)                          
    #Forrszemből LukasztoCylinder kivonása
bpy.ops.object.modifier_add(type='BOOLEAN')
bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["LukasztoCylinder"]
bpy.ops.object.modifier_apply(modifier="Boolean")

#cutting holes into the Line
    #Line kijelölés
ob = bpy.context.scene.objects["Line"]       
bpy.ops.object.select_all(action='DESELECT') 
bpy.context.view_layer.objects.active = ob   
ob.select_set(True)
    #Line konvertálása mesh-sé
bpy.ops.object.convert(target='MESH')                          
    #Lineból LukasztoCylinder kivonása
bpy.ops.object.modifier_add(type='BOOLEAN')
bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["LukasztoCylinder"]
bpy.ops.object.modifier_apply(modifier="Boolean")

#LukasztoCylinder törlése
ob = bpy.context.scene.objects["LukasztoCylinder"]       
bpy.ops.object.select_all(action='DESELECT') 
bpy.context.view_layer.objects.active = ob   
ob.select_set(True)

bpy.ops.object.delete(use_global=False, confirm=False)

#Assign material
objLine.active_material = materialGray
objSurface.active_material = materialGreen
objForrszem.active_material = materialGray