import bpy
import os
import random
import pandas as pd
from datetime import datetime
import sys
Operators = bpy.data.texts["Operators.py"].as_module()

Operators.register()

# clear previous images
collection = bpy.data.collections.get('Collection')
for obj in collection.objects:
    bpy.data.objects.remove(obj, do_unlink=True)

# add sequence editor for sound
scene = bpy.context.scene 
if not scene.sequence_editor:
    scene.sequence_editor_create()

def set_animation(img, start_frame, transition_frame, end_frame, i, len):
    
    # set starting location
    img.keyframe_insert(frame=start_frame, data_path='location')
    
    # move image in
    stack_margin = (i-len)*0.02 # visual "stack" offset effect
    img.location = (5+stack_margin, 0.0, stack_margin)
    movement_end = int(start_frame + round(fpi * 0.1))
    img.keyframe_insert(data_path='location', frame=movement_end)
    
    # play sound after movement
    sound = scene.sequence_editor.sequences.new_sound("swisher", directory_name, channel=3, frame_start=movement_end)
    sound.speed_factor = random.uniform(0.5, 2.0)
    # > Blender 3.3: sound.speed_factor
    # < Blender 3.3: sound.pitch 
    
    # keep image in same position (so you can look at it)
    img.keyframe_insert(data_path='location', frame=transition_frame)
    
    # move image down
    img.location = (5, 0.0, -5)
    img.keyframe_insert(data_path='location', frame=end_frame)


Operators.get_date_input()
sdate = datetime(2023,5,1)   # start date (inclusive)
edate = datetime(2023,5,31)  # end date   (inclusive)
date_list = pd.date_range(sdate, edate,freq='d')
date_dict = {}
num_total_images = 0

# import images, set up structures
for date in date_list:
    date_str = f"{date.year}.{date.month}.{date.day}"
    directory_name = select_folder_and_wait()
    folder_name = os.path.join(directory_name, date_str)
    
    images_in_current_date = []
    
    for file in os.scandir(folder_name):
        prefix, postfix = file.name.split('.')
        if postfix.lower() not in ['mov', 'mp4']: # skip videos with postfix
            bpy.ops.import_image.to_plane(files=[{"name":(file.name)}], directory=folder_name)
            images_in_current_date.append( bpy.data.objects[prefix] )
        
    num_total_images += len(images_in_current_date)
    date_dict[date] = images_in_current_date

# animation data
total_animation_length = 60                 # in seconds
intro_time, outro_time = 5, 5               # X seconds of in-out animation
fps = bpy.context.scene.render.fps          # current fps
start_offset_frame = intro_time * fps       # where to start displaying images
remaining_frames = (total_animation_length - intro_time - outro_time) * fps
fpi = remaining_frames / (num_total_images + len(date_list)) # frames per image; how much time 1 image will take up
# after each date an animation will play that is fpi frames long

index = 0
for date in date_dict:
    images = date_dict[date]
    cumulative_images_to_show = index + len(images) + 1
    ending_frame = start_offset_frame + (cumulative_images_to_show * fpi)
    transition_frame = ending_frame - fpi
    
    for i, image in enumerate(images):
        starting_frame = start_offset_frame + (fpi * index)
        set_animation(image, starting_frame, transition_frame, ending_frame, i, len(images))
        index += 1
    index += 1  # each transition takes the time of 1 image (fpi)
                # transition will count as image for purposes of calculation