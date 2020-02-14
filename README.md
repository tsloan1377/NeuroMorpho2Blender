# NeuroMorpho2Blender
Python scripts to load swc files from openneuromorpho.org into Blender

This Jupyter notebook and accompanying Python script allow users to programmatically access neuronal reconstructions from the OpenNeuroMorpho.org database.

Images and 3D models of the neurons can be previewed in the notebook. 
An animation of the neuron can also be rendered in Blender 2.8 using a headless instance of Blender.

If Blender 2.8 is already installed, the trickiest part of the process is making sure that the relevant packages are installed in the Blender Python installation (not the same as the Python environment used with Jupyter)

To do this, open a command prompt and navigate to where blender is installed, i.e.

cd path to blender\2.80\python\bin
  
The ensure pip is there:

python.exe -m ensurepip

Then install the missing dependencies, (Pandas, neuromirpholib)

python.exe -m pip install pandas --user
python.exe -m pip install neuromorpholib --user


