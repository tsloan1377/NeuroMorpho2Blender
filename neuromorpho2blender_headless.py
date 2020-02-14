# A script to run in Blender 2.8 to load a select neuron from NeuroMorpho.org

import bpy
import pandas as pd
import pickle
import random
import os
import math

from datetime import datetime
from neuromorpholib import neuromorpho
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

SCALE_F = 10  # factor to downscale the data

BASE_URL = 'http://neuromorpho.org/api'
TEMP_PATH = 'tmp_neuron.swc'
BLEND_SAVEPATH = 'neurID_' + str(argv) + '.blend'
RENDER_PATH = "Y://Renders/Blender/headless/" #"<my_path>/"

DEC_RATIO = 1 #ratio to decimate each mesh
SOLID_THICKNESS = 0.05

RENDER = True
ANIMATION = False
# Function definitions

# I've scraped data for the first 121544 neurons so you don't have to. 

def load_data(n_neurons = 121544): 

   # This section makes the code harder for other to use without downloading also these datafiles
    #n_neurons = 10000 #121544
    filename = 'first_'+str(n_neurons)+'_neurons_'
    df = pd.read_pickle(filename+'df.pkl') 

    with open(filename+'measurments_list.pkl', 'rb') as f:
        measurements = pickle.load(f)
        
    with open(filename+'info_listdf.pkl', 'rb') as f:
        info = pickle.load(f)    

    return df, measurements, info


def download_neuron(this_neuron):

    this_row = df.loc[df['neuron_id'] == this_neuron]

    neur_ind = this_row.index[0] # Distinct from this_neuron, but one value off. This is the value used to index the lists collected previously.
                                # zero-indexed to remove dtype of pandas index

    # Based on the id, get the neuron name, archive, and image url
    this_name = info[neur_ind]['neuron_name']
    this_archive = info[neur_ind]['archive']
    this_url = info[neur_ind]['png_url']

    # Use neuromorpho to get the associated swc file
    nmo = neuromorpho.NeuroMorpho()
    test_swc = nmo.download_swc(this_archive, this_name, text_only=True)

    #print(test_swc)
    # Save the swc locally as a temporary file (Otherwise save as a named file)
    text_file = open(TEMP_PATH, "wt")
    n = text_file.write(test_swc)
    text_file.close()

    return df


def load_neuron(this_neuron):

    # Load the temp neuron swc     
    f = open(TEMP_PATH) # Load the temp neuron swc
    lines = f.readlines()
    f.close()

    # find starting point '''
    x = 0
    while lines[x][0] is '#':
        x += 2  # Because neuromorpho.orgs standard is double spaced swc files
        
    # Create a dictionary with the first item '''
    data = lines[x].strip().split(' ')   # Space as separator for Allen BigNeuron, neuromorpho   
    #data = lines[x].strip().split('\t')   # Tab as separator for Janelia Mouselight

    neuron = {float(data[0]): [float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5]), float(data[6])]}
    x += 2
        
    # Read the rest of the lines to the dictionary '''
    for l in lines[x:]:
        data = l.strip().split(' ') # Space as separator for Allen BigNeuron
        #data = l.strip().split('\t')# Tab as separator for Janelia Mouselight

        if(len(data) == 7):    # Expecting 7 columns in swc file (skips empty lines)
            neuron[float(data[0])] = [float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5]), float(data[6])]
        
        
        
    bpy.ops.object.empty_add(type='ARROWS', location=(0.0, 0.0, 0.0), rotation=(0, 0, 0))
    a = bpy.context.selected_objects[0]    
    
    a.name = 'neuron_' + str(this_neuron)


    last = -10.0
    
    # Create object '''
    for key, value in neuron.items():
        
        if value[-1] == -1:
            continue
        
        if value[0] == 10:
            continue

        if (value[-1] != last):
             # trace the origins
            tracer = bpy.data.curves.new('tracer','CURVE')
            tracer.dimensions = '3D'
            spline = tracer.splines.new('BEZIER')

            curve = bpy.data.objects.new('curve',tracer)
            bpy.context.collection.objects.link(curve)   # Since 2.8, this is the way to do this
                 
            # render ready curve
            tracer.resolution_u = 8
            tracer.bevel_resolution = 8 # Set bevel resolution from Panel options
            tracer.fill_mode = 'FULL'
            tracer.bevel_depth = 0.001 # Set bevel depth from Panel options
            
            # move nodes to objects
            p = spline.bezier_points[0]
            p.co = [neuron[value[-1]][3] / SCALE_F, neuron[value[-1]][2] / SCALE_F, neuron[value[-1]][1] / SCALE_F]
            p.handle_right_type='VECTOR'
            p.handle_left_type='VECTOR'
            
            if (last > 0):
                spline.bezier_points.add(1)            
                p = spline.bezier_points[-1]
                p.co = [value[3]/SCALE_F, value[2]/SCALE_F, value[1]/SCALE_F]
                p.handle_right_type='VECTOR'
                p.handle_left_type='VECTOR'

            curve.parent = a
        
        if value[-1] == last:
            spline.bezier_points.add(1)
            p = spline.bezier_points[-1]
            p.co = [value[3]/SCALE_F, value[2]/SCALE_F, value[1]/SCALE_F]
            p.handle_right_type='VECTOR'
            p.handle_left_type='VECTOR'
        
        last = key
        
    return a.name

def combine_curves(this_neuron):
    context = bpy.context
    scene = context.scene
    o = bpy.context.scene.objects[this_neuron]#curr_neuron]  # This refers to the name of the object (string)
    # deselect all
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = o
    # select all children recursively
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    # select parent too
    o.select_set(state=True)
    context.view_layer.objects.active = context.selected_objects[1]    
    # join them
    bpy.ops.object.join()
    


def mesh_and_decimate(this_neuron, DEC_RATIO):
 
    o = bpy.context.scene.objects[this_neuron]#curr_neuron] 
    
    for child in o.children:
        # Convert to mesh
        bpy.ops.object.convert(target='MESH')    
        
        # Decimate the mesh
        modifierName='DecimateMod'
        modifier=child.modifiers.new(modifierName,'DECIMATE')
        modifier.ratio=DEC_RATIO
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
        
        # Solidify the mesh
        modifierName='SolidifyMod'
        modifier=child.modifiers.new(modifierName,'SOLIDIFY')
        modifier.thickness=SOLID_THICKNESS
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")

def color_heir(ob, mat):     
    for child in ob.children:
      
        child.data.materials.append(mat) #add the material to the object 


        
        
# Control flow
if __name__ == "__main__":

    df, measurements, info = load_data() # Load pcikled dataframes
    neurons = argv # Get neuron id(s) from input arguments
       
    for i in range(len(neurons)):    # The way I can do it so it's easier to hack to test smaller numbers
        
        curr_neuron = int(neurons[i])           # Remember to remove this if doing the loop in a more pythonic way. (Using: for curr_neuron in neurons)
        print('curr_neuron:' ,curr_neuron)
        
        # In each case below, curr_neuron is a string
        download_neuron(curr_neuron)
        neur_name = load_neuron(curr_neuron)
        combine_curves(neur_name)#curr_neuron)
        mesh_and_decimate(neur_name, DEC_RATIO)#curr_neuron, DEC_RATIO)

        # Get the object identified by the string
        ob = bpy.context.scene.objects[neur_name]
        

        print(i,curr_neuron, 'at: ', datetime.now())
        
        # Do material in same loop
        
        mat = bpy.data.materials.new(name=neur_name)#curr_neuron) #set new material to variable
        mat.diffuse_color = (random.random(), random.random(), random.random(), 1) # Simplest method is to create diffuse colored shader.
        
        
        
        # Extra steps for the material to create an emission shader.
        # get the nodes
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
            
        # clear all nodes to start clean
        nodes.clear()
        
        # create emission node
        node_emission = nodes.new(type='ShaderNodeEmission')
        node_emission.inputs[0].default_value = (random.random(),random.random(),random.random(),1)  # green RGBA
        node_emission.inputs[1].default_value = 10 # strength
        node_emission.location = 0,0
        
        # create output node
        node_output = nodes.new(type='ShaderNodeOutputMaterial')   
        node_output.location = 400,0   
        
        # link nodes
        links = mat.node_tree.links
        link = links.new(node_emission.outputs[0], node_output.inputs[0])

        # Apply material to all
        for child in ob.children:
        
            child.data.materials.append(mat) #add the material to the object 
          
        
        # Center the camera view on the neuron
        bpy.ops.view3d.camera_to_view_selected()
        

        bpy.ops.wm.save_mainfile(filepath=BLEND_SAVEPATH)
        print('Finished saving blend file.')   
           
        # Rendering
        
        if RENDER:
            print("Rendering single frame with Cycles")
            # Render with Cycles (Single frame)
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles_curves.use_curves = True   # Makes sure it renders the hairs
            bpy.context.scene.cycles.device = 'GPU'
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.filepath = RENDER_PATH +str(argv)+'_cycles'
            bpy.context.scene.frame_end = 1
            bpy.ops.render.render(animation=True)
            print('Done rendering cycles.')   
            

            if ANIMATION:
                print("Rendering animation with EEVEE")
                bpy.context.scene.render.engine = 'BLENDER_EEVEE'
                bpy.context.scene.render.image_settings.file_format = 'FFMPEG'    #'AVI_JPEG'
                bpy.context.scene.frame_end = 360
                bpy.context.scene.render.filepath = RENDER_PATH+str(argv)+'_anim_'
      
                bpy.ops.render.render(animation=True)#,use_viewport=True)
                print('Done rendering eevee.')      
            
 
            print('Finished rendering.')
 