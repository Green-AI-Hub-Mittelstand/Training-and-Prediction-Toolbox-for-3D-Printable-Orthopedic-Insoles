import numpy as np
import pandas as pd
import cv2
import imageio
from io import BytesIO
from django.core.files.base import ContentFile

def crop_plate(frames_3d):
    
    deleted_rows = 0
    #delete rows
    for i in range(frames_3d.shape[0]):
        adjusted_index = i - deleted_rows
        if adjusted_index < frames_3d.shape[2] and np.sum(frames_3d[:,:,adjusted_index]) == 0:
            frames_3d = np.delete(frames_3d, adjusted_index, axis=2)
            deleted_rows += 1
    
    deleted_columns = 0
    # delete columns
    for i in range(frames_3d.shape[1]):
        adjusted_index = i - deleted_columns
        if adjusted_index < frames_3d.shape[1] and np.sum(frames_3d[:,adjusted_index,:]) == 0:
            frames_3d = np.delete(frames_3d, adjusted_index, axis=1)
            deleted_columns += 1
    return frames_3d




def scale_frame(img,width = 256, height = 128):
    assert(width % 64 == 0) #
    assert(height % 32 == 0)
    desired_size = (width,height)  # for example
    ratio = [new_dim / old_dim for new_dim, old_dim in zip(desired_size, img.shape[:2])]
    resized_image = cv2.resize(img, None, fx=ratio[1], fy=ratio[0], interpolation=cv2.INTER_AREA)
    return resized_image

#creates gif np array 
def render_foot_gif(data):
    #turn features(min,max,etc) which were rows before into columns
    data = data.T
    #replace superfluous head with feature names
    data.columns = data.iloc[0] 
    data = data.drop(data.index[0])


    frames = []
    #delete measurements that are not part of the timelapse
    del data['20%-Durchschnitt']
    del data['Minimum']
    del data['Maximum']

    for time in range (0,len(data.iloc[1,:])):
      #measuring plate at a given time
      sensors = data.iloc[:,time]

      if(sum(sensors)>0):
        #np.array(image) of the measuring plate
        measuring_plate = np.reshape(sensors.to_numpy().astype(float), (64, 32))
        frames.append(measuring_plate)     
      
    #resize each frame because original is very small
    frames_3d = np.stack(frames, axis=0)
    
    # crop the image so that only the rows and columns are visible where at least one senser was activated
    #frames_3d = crop_plate(frames_3d)
    heatmaps = []
    
    counter = 0
    
    for i in range(frames_3d.shape[0]):
        frame = frames_3d[i]
        
        counter+=1
        
        #normalize the frame for better visualization
        normalized_frame = cv2.normalize(frame, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        #greyscale to heatmap leads to the sensors with the most pressure being blue, thus invert the image
        normalized_frame = cv2.bitwise_not(normalized_frame)
        #create heatmap
        heatmap = cv2.applyColorMap(normalized_frame, cv2.COLORMAP_JET)

        #apply the mask to the image so that sensors around foot are not blue
        heatmap[frame <= 0] = [0, 0, 0]
        
        #scale the frames
        heatmap = scale_frame(heatmap)

        heatmaps.append(heatmap)

    # convert the list of heatmaps to an array
    heatmaps_array = np.array(heatmaps)


    return (counter, heatmaps_array)
 
 
 
def scale_up_image(image, scale_factor):
    # Get the dimensions of the original image
    original_height, original_width = image.shape[:2]
    
    # Calculate the new dimensions after scaling
    new_height = int(original_height * scale_factor)
    new_width = int(original_width * scale_factor)
    
    # Use linear interpolation to scale up the image
    scaled_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)
    for i in range(new_height):
        for j in range(new_width):
            y = i / scale_factor
            x = j / scale_factor
            scaled_image[i, j] = image[int(y), int(x)]
    
    return scaled_image

from participants.models import UploadedFile
from ..models import AnimatedPressure


def createAnimationForCSV(uploadedFile_id):
    ufile = UploadedFile.objects.get(id=uploadedFile_id)
    
    try:
    
        if ufile.animation != None:             # we are skipping this is there is already a video
            return
    except:
        pass
    
    
    
    
    ap = AnimatedPressure.objects.create(uploadedFile=ufile)
    
    # try and load the csv
    data = pd.read_csv(ufile.file.path, sep =';',decimal=',')
    
    (num_frames, ani) = render_foot_gif(data)
    
    # get the middle one
    
    middle = None
        
    
    #output_file = 'output_video.mp4'
    
    gif_bytesio = BytesIO()

    # Create a writer object to write the video
    writer = imageio.get_writer(gif_bytesio, format="mp4", fps=25)  # You can adjust the fps as needed

    # Iterate through each image and add it to the video
    
    for (i,image) in enumerate(ani):
        x = scale_up_image(image,3)
        writer.append_data(x)
        if(num_frames/2 == i):
            middle = scale_up_image(image,3)

    # Close the writer
    writer.close()
    
    ap.animation.save("animation-%s.mp4" % ap.id, ContentFile(gif_bytesio.getvalue()), save=True)
    ap.save()
    
    if not middle is None:    
        static_bytesio = BytesIO()
        
        imageio.imwrite(static_bytesio, middle, format='jpg')
        ap.animationPoster.save("animation-%s.jpg" % ap.id, ContentFile(static_bytesio.getvalue()), save=True)

    ap.save()
    
    
from celery import shared_task
@shared_task
def createAnimationForCSVAsync(uploadedFile_id):
    createAnimationForCSV(uploadedFile_id)
