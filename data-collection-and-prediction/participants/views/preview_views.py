from django.shortcuts import render
from dataCollection.generalHelpers import dimensions
from dataInspection.models import TrainingData

from participants.decorators import admin_required
from participants.helpers.render import create20PercentImageFromCSV, create20PercentImageFromCSVForMapping, extractRowFromCSV
from ..models import *

from django.http import JsonResponse, HttpResponse
from ..models import UploadedFile


from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.conf import settings
import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image, ImageDraw
from io import BytesIO
import cv2
from django.views.decorators.cache import cache_page


cache_duration = 60*10

@cache_page(cache_duration)
@admin_required
def preview_upload(request, id):

    # Get the UploadedFile instance based on the provided id
    uploaded_file = get_object_or_404(UploadedFile, id=id)

    context = {
        'file':uploaded_file
    }

    # Check if the user is an admin (staff member)
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to access this file.")

    # Build the file path
    file_path = uploaded_file.file.path

    file_extension = os.path.splitext(file_path)[1].lower()
    print(file_extension)

    if file_extension in [".png",".bmp",".jpg"]:
        return render(request, 'preview/preview_image.html', context)

    if file_extension in [".csv",]:
        return render(request, 'preview/preview_csv.html', context )


    # Open the file and create an HttpResponse with the file content
    with open(file_path, 'rb') as file:
        pass

        #response = HttpResponse(file.read(), content_type='application/force-download')
        #response['Content-Disposition'] = f'attachment; filename={uploaded_file.file.name}'

    return render(request, 'preview/preview_generic.html', context)



@cache_page(cache_duration)
@admin_required
def render20percentNativeCSV(request, id, row=2):
    uploaded_file = get_object_or_404(UploadedFile, id=id)
    color = request.GET.get('color',"red")

    image = create20PercentImageFromCSV(uploaded_file.file.path, row, color, True)

    # Save the image to a BytesIO object
    image_io = BytesIO()
    image.save(image_io, format="PNG")
    image_io.seek(0)

    image_data = image_io.read()

    # Create an HTTP response with the image
    response = HttpResponse(image_data, content_type="image/png")


    response['Content-Disposition'] = "inline; filename=%s.png" % (uploaded_file.id,)
    response['X-Content-Type-Options'] = 'nosniff'  # Add this header to prevent MIME type sniffing

    return response


def im2resp(result):
    # Save the image to a BytesIO object

    result_pil = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))


    result_io = BytesIO()
    result_pil.save(result_io, format='PNG')
    result_io.seek(0)

    # Create an HTTP response with the image
    response = HttpResponse(result_io, content_type="image/png")


    response['Content-Disposition'] = "inline; filename=%s.png" % (id,)
    response['X-Content-Type-Options'] = 'nosniff'  # Add this header to prevent MIME type sniffing

    return response


def padPressureImage(img, total_size=3000):
    blank_image = np.zeros((total_size, total_size, 4), dtype=np.uint8)
    #blank_image[:, :, 3] = 0
    rows, cols, _ = img.shape
    x_offset = int((total_size - cols) / 2)
    y_offset = int((total_size - rows) / 2)

    blank_image[y_offset:y_offset + rows, x_offset:x_offset + cols, :4] = img
    #blank_image[:, :, 3] = 150  # Set alpha channel to fully opaque for the rotated image

    return blank_image



import math

# def getBoundingBoxInFoamCoordinates(pressure_image, t_x, t_y, alpha_rad):
#     (w,h) = pressure_image.size
#     p_1_x = t_x + (w/2.0) * math.cos(alpha_rad) - (h/2.0) * math.sin(alpha_rad)
#     p_1_y = t_y + (w/2.0) * math.sin(alpha_rad) - (h/2.0) * math.cos(alpha_rad)

#     p_2_x = t_x + (w/2.0) * math.cos(alpha_rad) + (h/2.0) * math.sin(alpha_rad)
#     p_2_y = t_y + (w/2.0) * math.sin(alpha_rad) + (h/2.0) * math.cos(alpha_rad)

#     p_3_x = t_x - (w/2.0) * math.cos(alpha_rad) + (h/2.0) * math.sin(alpha_rad)
#     p_3_y = t_y - (w/2.0) * math.sin(alpha_rad) + (h/2.0) * math.cos(alpha_rad)

#     p_4_x = t_x - (w/2.0) * math.cos(alpha_rad) - (h/2.0) * math.sin(alpha_rad)
#     p_4_y = t_y - (w/2.0) * math.sin(alpha_rad) - (h/2.0) * math.cos(alpha_rad)

#     return ((p_1_x, p_1_y), (p_2_x, p_2_y), (p_3_x, p_3_y), (p_4_x, p_4_y),  )



@admin_required
def renderMappingOnFoam(request, id):
    training_file = get_object_or_404(TrainingData, id=id)

    print("Participant", training_file.participant.id)

    t_x = training_file.pressure_x
    t_y = training_file.pressure_y
    alpha = training_file.pressure_rot
    alpha_rad = math.radians(360-alpha)

    print("X: %s\nY: %s\nRot: %s" % (t_x, t_y, alpha))

    pressure_image = create20PercentImageFromCSV(training_file.pressurePlate.uploadedFile.file.path, 2,"green", (100,0,0,0), (50,50,50,150))

    (w,h) = pressure_image.size



def calculateProjectionMatrix(w,h,t_x, t_y, alpha_rad):
    p_1_x = t_x + (w/2.0) * math.cos(alpha_rad) - (h/2.0) * math.sin(alpha_rad)
    p_1_y = t_y - (w/2.0) * math.sin(alpha_rad) - (h/2.0) * math.cos(alpha_rad)

    p_2_x = t_x + (w/2.0) * math.cos(alpha_rad) + (h/2.0) * math.sin(alpha_rad)
    p_2_y = t_y - (w/2.0) * math.sin(alpha_rad) + (h/2.0) * math.cos(alpha_rad)

    p_3_x = t_x - (w/2.0) * math.cos(alpha_rad) + (h/2.0) * math.sin(alpha_rad)
    p_3_y = t_y + (w/2.0) * math.sin(alpha_rad) + (h/2.0) * math.cos(alpha_rad)

    p_4_x = t_x - (w/2.0) * math.cos(alpha_rad) - (h/2.0) * math.sin(alpha_rad)
    p_4_y = t_y + (w/2.0) * math.sin(alpha_rad) - (h/2.0) * math.cos(alpha_rad)


    q_1_x = w
    q_1_y = 0

    q_2_x = w
    q_2_y = h

    q_3_x = 0
    q_3_y = h

    q_4_x = 0
    q_4_y = 0

    offset_x = 0 #-cols_cropped_right * sensorSizeInPx
    offset_y = 0 #-cols_cropped_left * sensorSizeInPx

    src_points = np.float32([[p_1_x + offset_x, p_1_y + offset_y], [p_2_x + offset_x, p_2_y + offset_y],[p_3_x + offset_x, p_3_y + offset_y],[p_4_x + offset_x, p_4_y + offset_y],])
    dst_points = np.float32([[q_1_x, q_1_y], [q_2_x, q_2_y],[q_3_x, q_3_y],[q_4_x, q_4_y],])

    perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    return perspective_matrix

def applyShift(matrix, shift_x, shift_y):
    shifted_matrix = matrix.copy()
    shifted_matrix[:, 2] += [shift_x, shift_y, 0]

    return shifted_matrix


def getProjetionMatrixFromTrainingData(trainig_data_id, _apply_shift=False):
    training_file = get_object_or_404(TrainingData, id=trainig_data_id)
    t_x = training_file.pressure_x
    t_y = training_file.pressure_y
    alpha = training_file.pressure_rot
    alpha_rad = math.radians(360-alpha)
    
    (pressure_image_original, pressure_image, crop_amount) = create20PercentImageFromCSVForMapping(training_file.pressurePlate.uploadedFile.file.path, 2,"green", (100,0,0,0), (50,50,50,150))
    (w,h) = pressure_image.size
    
    sensorSizeInPx = dimensions.mm2pixel(settings.SENSOR_SIZE)
    (rows_cropped_top, rows_cropped_bottom, cols_cropped_left, cols_cropped_right) = crop_amount
    
    perspective_matrix = calculateProjectionMatrix(w,h,t_x, t_y, alpha_rad)
    
    if _apply_shift:
        perspective_matrix = applyShift(perspective_matrix, sensorSizeInPx*cols_cropped_left, sensorSizeInPx*rows_cropped_top )
    
    return perspective_matrix



def getMappedTrainingData(training_data_id):
    training_file = get_object_or_404(TrainingData, id=training_data_id)
    perspective_matrix = getProjetionMatrixFromTrainingData(training_data_id,True)
    
    
    mappedPoints = []
    
    sensorSizeInPx = dimensions.mm2pixel(settings.SENSOR_SIZE)
    scalingFactor = 1.0 / (sensorSizeInPx )

        
    
    for point in training_file.footPrintPoints:


        input_point = np.float32([[point.x, point.y]])
        # Use the perspective matrix to transform the input point

        input_point_reshaped = input_point.reshape(-1, 1, 2)
        resulting_point = cv2.perspectiveTransform(input_point_reshaped, perspective_matrix)
        mappedPointScaled = (resulting_point[0][0][0] , resulting_point[0][0][1])
        mappedPointNormalized = (resulting_point[0][0][0] * scalingFactor, resulting_point[0][0][1]*scalingFactor)
              
        p = {
            "points":mappedPointNormalized,
            "pointType":point.pointType
        }
        
        mappedPoints.append(p)
        
    
    csvRow = extractRowFromCSV(training_file.pressurePlate.uploadedFile.file.path, 2, False)
    return (mappedPoints, csvRow)

import os, json
from ..serializers import *

def jsonToFile(data, filename):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=2)

import csv

def csvDataToFile(data, filename):
    # Path to the CSV file
    csv_file_path = filename

    # Writing array to CSV file
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

import shutil

def compileParticipantInDir(green_ai_id, directory, add_video=False):
    participant = get_object_or_404(Participant, public_id=green_ai_id)
    
    participant_dir = os.path.join(directory,str(green_ai_id))
    os.makedirs(participant_dir, exist_ok=True)
    
    # serialize the participant
    pSerialized = ParticipantSerializerML(participant).data
    jsonToFile(pSerialized, os.path.join(participant_dir,str(green_ai_id)+".json"))
    #with open(os.path.join(participant_dir,str(green_ai_id)+".json"), "w") as json_file:
    #    json.dump(pSerialized, json_file, indent=2)
        
    for (foot, uploadTypes) in [("left",[UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_WALK_L]),("right",[UploadedFile.PRESSURE_SWAY_R, UploadedFile.PRESSURE_WALK_R])]:
        dataDir = os.path.join(participant_dir, "feet",foot)
        os.makedirs(dataDir, exist_ok=True)
        
        insole = None
        if foot == "left":
            insole = participant.leftInsole
            insoleData = InsoleParametersMlLeft(insole).data
        else:
            insole = participant.rightInsole
            insoleData = InsoleParametersMlRight(insole).data
            
            
        insoleData["foot"] = foot
        jsonToFile(insoleData, os.path.join(dataDir,"insole.json") )
            
        # safe insole to dir
        
    
        samplesDir = os.path.join(dataDir, "samples")
        for dataEntry in participant.trainingData.filter(pressure_type__in=uploadTypes):
            # create dir for data entry              
            (mappedPoints, csvRow) = getMappedTrainingData(dataEntry.id)     
            
            sampleDir = os.path.join(samplesDir, str(dataEntry.id))            
            os.makedirs(sampleDir, exist_ok=True)
            
            csvFilename = os.path.join(sampleDir, "pressure.csv")
            csvDataToFile([csvRow], csvFilename)
            
            rawCsvFilePathLocal = dataEntry.pressurePlate.uploadedFile.file.path
            rawCsvFilename = os.path.join(sampleDir, "raw_pressure.csv")
            shutil.copyfile(rawCsvFilePathLocal, rawCsvFilename)
            
            if add_video:
                # check if there is a video
                animationPath = None
                try:
                    animationPath = dataEntry.pressurePlate.uploadedFile.animation.animation.path
                except:
                    pass
                
                if animationPath != None:
                    animationFilename = os.path.join(sampleDir, "animation.mp4")
                    shutil.copyfile(animationPath, animationFilename)
                
            pointsFilename = os.path.join(sampleDir, "points.json")
            jsonToFile(mappedPoints, pointsFilename)
            
            metaFilename = os.path.join(sampleDir, "meta.json")
            meta = TrainingDataML(dataEntry).data
            jsonToFile(meta, metaFilename)
            
        
import tempfile
import os
import zipfile
from django.http import HttpResponse


def compileParticipantDataAsZip(green_ai_id, add_video=False):
    
    """
    - 54
        - 54.json - questionnaire and comments
        - feet
            - left
                - insole.json
                - samples
                    - x
                        - pressure.csv
                        - points.json - coords and type
                        - meta.json - fit_quality, pressure_type, id
            - right 
                - ...
    """
    base_participant_dir = "./__participants/"
    
    temp_dir = tempfile.TemporaryDirectory()

    # Access the path of the temporary directory
    temp_dir_path = temp_dir.name

    # Now you can use this path as needed
    print("Temporary directory path:", temp_dir_path)
    
    compileParticipantInDir(green_ai_id, temp_dir_path, add_video)
    
    pass


from django.conf import settings
from django.http import JsonResponse

def readonly_secret_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        readonly_secret_header = request.headers.get('ReadOnlySecret')
        if readonly_secret_header != settings.READ_ONLY_SECRET:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@readonly_secret_required
def downloadTrainingData(request, id):
    params = request.GET
    
    add_video = False
    
    if 'add_video' in params and params['add_video'].lower() == '1':
        add_video = True
    else:
        add_video = False
    
    
    temp_dir = tempfile.TemporaryDirectory()
    # Access the path of the temporary directory
    temp_dir_path = temp_dir.name
    
    
    
    compileParticipantInDir(id, temp_dir_path, add_video)
    
    zip_file_path = os.path.join(tempfile.gettempdir(), 'temp_files.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(temp_dir.name):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, temp_dir.name))

    # Open the zip file and serve it for download
    with open(zip_file_path, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="'+str(id)+'.zip"'
        return response


import math 

def renderMappedTrainingData(mappedPoints, csvRow, scale = 1):
    dot_color = "red"
    background_color=(20,20,20,0)
    blank_dot_color=(100,100,100)
    
    markedPointRadius = math.ceil(0.2*scale)
    pressurePointRadiusMax = math.ceil(0.5*scale)
    pressurePointRadiusMin = math.ceil(0.1*scale)
    minimalRadius = math.ceil(0.025*scale)
    
    original_image_array = np.array(csvRow).reshape(64, 32) # todo - this might break
    (shape_y, shape_x) = original_image_array.shape


    width = shape_x*scale  # this is the width of the pressure plate / 2
    height = shape_y*scale
    image = Image.new("RGBA", (width, height),background_color)

    # Create a drawing object
    draw = ImageDraw.Draw(image)


    # Set the radius of the circle
    radius = 10

    # Flatten the array to a 1D array
    flat_data = original_image_array.flatten()

    # Remove non-positive numbers
    positive_numbers = flat_data[flat_data > 0] # why would there be non positive numbers?

    # Find the largest and smallest positive numbers
    largest_positive = np.max(positive_numbers)
    smallest_positive = np.min(positive_numbers)




    for x in range(0,shape_x):
        for y in range(0,shape_y):
            val = original_image_array[y][x]

            center_x = round(scale/2 + (x * scale))
            center_y = round(scale/2 + (y * scale))

            if val > 0:    
                radius = int(dimensions.map(val, smallest_positive, largest_positive, pressurePointRadiusMin,pressurePointRadiusMax ))

                draw.ellipse(
                    [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                    fill=dot_color,
                    outline=dot_color,
                )
            else:
                radius = minimalRadius
                draw.ellipse(
                    [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                    fill=blank_dot_color,
                    outline=None,
                )     

    

    # now draw the points
    for point in mappedPoints:
        print(point)
        (x,y) = point['points']
        pType = point['pointType']

        radius = markedPointRadius
        
        (x,y) = (x*scale, y*scale)

        draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=(0,255,0))        
    return image


@admin_required
def renderRawTrainingData(request, training_data_id, scale=1):
    (points,csvData) = getMappedTrainingData(training_data_id)
    image = renderMappedTrainingData(points, csvData, scale)
    
    image_buffer = BytesIO()
    #cropped.save(image_buffer, format="PNG")
    image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    # Create an HttpResponse with the image
    response = HttpResponse(content_type="image/png")
    response.write(image_buffer.read())

    return response

def _renderMapping( id):
    training_file = get_object_or_404(TrainingData, id=id)

    print("Participant", training_file.participant.id)

    t_x = training_file.pressure_x
    t_y = training_file.pressure_y
    alpha = training_file.pressure_rot
    alpha_rad = math.radians(360-alpha)

    print("X: %s\nY: %s\nRot: %s" % (t_x, t_y, alpha))

    sensorSizeInPx = dimensions.mm2pixel(settings.SENSOR_SIZE)


    (pressure_image_original, pressure_image, crop_amount) = create20PercentImageFromCSVForMapping(training_file.pressurePlate.uploadedFile.file.path, 2,"green", (100,0,0,0), (50,50,50,150))
    (rows_cropped_top, rows_cropped_bottom, cols_cropped_left, cols_cropped_right) = crop_amount
    #pressure_image = padPressureImage(pre)

    perspective_matrix = getProjetionMatrixFromTrainingData(id)


    ###################
    draw = ImageDraw.Draw(pressure_image, "RGBA")
    drawOrig = ImageDraw.Draw(pressure_image_original, "RGBA")



    for point in training_file.footPrintPoints:


        input_point = np.float32([[point.x, point.y]])
        # Use the perspective matrix to transform the input point

        input_point_reshaped = input_point.reshape(-1, 1, 2)
        print("---")
        print("Input point: %s" % input_point_reshaped)

        print(input_point_reshaped[0][0][0])
        print(input_point_reshaped[0][0][1])



        resulting_point = cv2.perspectiveTransform(input_point_reshaped, perspective_matrix)
        print("Resulting  point: %s" % resulting_point)
        print("---")
        print(" %s %s" % (resulting_point[0][0][0], resulting_point[0][0][1]))

        center = (resulting_point[0][0][0] , resulting_point[0][0][1])

        radius = 10

        fill_color = (255, 0, 0,125)
        #pressure_image = pressure_image.convert("RGBA")


        draw_offset_x = cols_cropped_left * sensorSizeInPx
        draw_offset_y = rows_cropped_top * sensorSizeInPx
        print("sensorSizeInPx")
        print(sensorSizeInPx)
        print("rows_cropped_top")
        print(rows_cropped_top)
        print("draw_offset_y")
        print(draw_offset_y)


        draw.ellipse([(center[0] - radius, center[1] - radius), (center[0] + radius, center[1] + radius)], fill=fill_color)
        perspective_matrix_shift = getProjetionMatrixFromTrainingData(id, True)
        resulting_point_shift = cv2.perspectiveTransform(input_point_reshaped, perspective_matrix_shift)
        center_shift = (resulting_point_shift[0][0][0] , resulting_point_shift[0][0][1])
        
        center = center_shift
        
        drawOrig.ellipse([(center[0]  - radius, center[1]  - radius), (center[0]+ radius, center[1]+ radius)], fill=fill_color)
        #drawOrig = ImageDraw.Draw(pressure_image_original, "RGBA")

    ########################

    return (pressure_image_original, pressure_image)



@admin_required
def renderMappingOrig(request, id):
    (orig, cropped) = _renderMapping(id)

    image_buffer = BytesIO()
    #cropped.save(image_buffer, format="PNG")
    orig.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    # Create an HttpResponse with the image
    response = HttpResponse(content_type="image/png")
    response.write(image_buffer.read())

    return response




@admin_required
def renderMappingCropped(request, id):
    (orig, cropped) = _renderMapping(id)

    image_buffer = BytesIO()
    cropped.save(image_buffer, format="PNG")
    #orig.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    # Create an HttpResponse with the image
    response = HttpResponse(content_type="image/png")
    response.write(image_buffer.read())

    return response



#@cache_page(cache_duration)
@admin_required
def renderAlignment(request, id):
    training_file = get_object_or_404(TrainingData, id=id)

    left = training_file.pressure_x
    top = training_file.pressure_y
    angle = training_file.pressure_rot

    print("X: %s\nY: %s\nRot: %s - %s" % (left, top, angle, training_file.foot))



    pressure_image = create20PercentImageFromCSV(training_file.pressurePlate.uploadedFile.file.path, 3,"green", (100,0,0,0), (0,200,250,150))
    pressure_image = np.array(pressure_image)

    padding = 3000


    padded_pressure_image = padPressureImage(pressure_image,padding)

    # Create a blank image with a transparent background (4 channels - RGBA)
    blank_image = np.zeros((padding, padding, 4), dtype=np.uint8)

    pink_color = np.array([255, 192, 203, 255], dtype=np.uint8)
    blank_image[:,:,: ] = pink_color


    # Load the foam print into the center
    foam_image = cv2.imread(training_file.footPrintFile)
    foam_rows, foam_cols, _ = foam_image.shape
    x_offset = int((padding - foam_cols) / 2)
    y_offset = int((padding - foam_rows) / 2)

    blank_image[y_offset:y_offset + foam_rows, x_offset:x_offset + foam_cols, :3] = foam_image



    # Set alpha channel to fully transparent
    blank_image[:, :, 3] = 0





    rows, cols, _ = padded_pressure_image.shape

    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), 360-angle, 1)
    rotated_image = cv2.warpAffine(padded_pressure_image, M, (cols, rows))

    print("Roated Image Shape")
    print(rotated_image.shape)

    rotated_rows, rotated_cols, _ = rotated_image.shape


    # first set the center to the top left of the foam image

    move_left = int(- (foam_cols / 2)) + left #+ int(rotated_rows/2) #+ left
    move_top = int(- (foam_rows / 2)) + top #+ int(rotated_cols/2) #+ top

    print("Move Left: %s" % move_left)
    print("Move Top: %s" % move_top)


    x_offset = int((padding - rotated_cols) / 2)  + move_left
    y_offset = int((padding - rotated_rows) / 2)+ move_top



    # Ensure that the overlay operation stays within the bounds of the blank image
    y_start = max(0, y_offset)
    x_start = max(0, x_offset)
    y_end = min(y_offset + rows, padding)
    x_end = min(x_offset + cols, padding)

    # Overlay the rotated image onto the blank image considering transparency
    for c in range(3):  # RGB channels
        blank_image[y_start:y_end, x_start:x_end, c] = \
            rotated_image[y_start - y_offset:y_end - y_offset, x_start - x_offset:x_end - x_offset, c] * (
                        rotated_image[y_start - y_offset:y_end - y_offset, x_start - x_offset:x_end - x_offset, 3] / 255.0) + \
            blank_image[y_start:y_end, x_start:x_end, c] * (
                        1.0 - rotated_image[y_start - y_offset:y_end - y_offset, x_start - x_offset:x_end - x_offset, 3] / 255.0)


    #blank_image[y_offset:y_offset + rows, x_offset:x_offset + cols, :4] = rotated_image
    #blank_image[:, :, 3] = 255  # Set alpha channel to fully opaque for the rotated image

    return im2resp(blank_image)



    numpy_array = np.array(pressure_image)

    # Convert RGB to BGR (OpenCV uses BGR by default)
    pressure_image = cv2.cvtColor(numpy_array, cv2.COLOR_RGB2BGR)



    pressure_image = cv2.copyMakeBorder(pressure_image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, None, (255,255,255))
    return im2resp(pressure_image)

    left = training_file.pressure_x
    top = training_file.pressure_y
    angle = training_file.pressure_rot


    # Ensure foam_image is the larger image

    height1, width1, _ = foam_image.shape
    height2, width2, _ = pressure_image.shape

    # Create a white canvas to overlay the images
    canvas = np.ones((width1*3, height1*3)) * 255

    # Calculate the rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(((width2 // 2), (height2 // 2)), 360-angle, 1)

    opencv_image_rotated = cv2.warpAffine(pressure_image, rotation_matrix, (width1, height1))

    return im2resp(opencv_image_rotated)

    translation_matrix = np.float32([[1, 0, left - width2//2], [0, 1, top - height2 //2]])

    opencv_image_translated = cv2.warpAffine(opencv_image_rotated, translation_matrix, (width1, height1))


    # Combine the images
    result = cv2.addWeighted(foam_image, 0.1, opencv_image_translated, 0.9, 0)
    #result = cv2.addWeighted(result, 0.5, opencv_image_translated, 0.5, 0)

    # Convert the result to PIL Image for saving



    return im2resp(result)


from PIL import Image, ImageEnhance
from django.http import HttpResponse
import io


def enhanceImage(imagePath, contrast=2, brightness=20):
    image = Image.open(imagePath)
    enhancer = ImageEnhance.Contrast(image)
    adjusted_image = enhancer.enhance(contrast)
    enhancer_brightness = ImageEnhance.Brightness(adjusted_image)
    adjusted_image = enhancer_brightness.enhance(brightness)

    # Convert PIL image to bytesIO
    image_io = io.BytesIO()
    adjusted_image.save(image_io, format='PNG')

    # Create Django HTTP response with image content
    response = HttpResponse(image_io.getvalue(), content_type='image/png')

    return response

@cache_page(cache_duration)
@admin_required
def renderEnhancedFootprint(request, participant_id, contrast=2, brightness=20, foot="left"):
    print(participant_id)
    p = get_object_or_404(Participant, public_id=participant_id)

    img_path = None

    if foot == "left":
        img_path = p.analyzedFoamPrint.leftFoot.path
    else:
        img_path = p.analyzedFoamPrint.rightFoot.path


    return enhanceImage(img_path,contrast, brightness)
