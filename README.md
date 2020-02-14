# NeuroMorpho2Blender
Python scripts to load swc files from neuromorpho.org into Blender

This Jupyter notebook and accompanying Python script allow users to programmatically access neuronal reconstructions from the NeuroMorpho.org database. 
For example, one can play neuro-roulette by finding random neurons:
http://neuromorpho.org/byRandom.jsp
Once you find one you like, find it's unique ID :
i.e for this neurons:
http://neuromorpho.org/neuron_info.jsp?neuron_name=4H-13traced-7
NeuroMorpho.Org ID : 	NMO_56794
Only the number "56794" is needed to download it's swc into Blender.

In addition to the files in this repo, additional summary data files must be downloaded from:
https://drive.google.com/drive/folders/1PMbQZ6UIU8ZXup8qidgtzbtOh_nNald8?usp=sharing

I am providing this summary so that the NeuroMorpho server doesn't get overloaded

Images and 3D models of the neurons can be previewed in the notebook. 
An animation of the neuron can also be rendered in Blender 2.8 using a headless instance of Blender.

If Blender 2.8 is already installed, the trickiest part of the process is making sure that the relevant packages are installed in the Blender Python installation (not the same as the Python environment used with Jupyter)

To do this, open a command prompt and navigate to where blender is installed, i.e.

"cd path_to_blender\2.80\python\bin"
  
The ensure pip is there:

<python.exe -m ensurepip>

Then install the missing dependencies, (Pandas, neuromirpholib):

<python.exe -m pip install pandas --user>
<python.exe -m pip install neuromorpholib --user>


