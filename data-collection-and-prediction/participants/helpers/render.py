from django.shortcuts import render

from participants.decorators import admin_required
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



from dataCollection.generalHelpers import dimensions

def crop_image(image, add_details=False):
    # Find the indices of the first and last non-zero values in each row
    row_nonzero = np.where(image.any(axis=1))[0]
    first_row, last_row = row_nonzero[0], row_nonzero[-1]

    # Find the indices of the first and last non-zero values in each column
    col_nonzero = np.where(image.any(axis=0))[0]
    first_col, last_col = col_nonzero[0], col_nonzero[-1]

    # Truncate the array based on the calculated indices
    cropped_image = image[first_row:last_row+1, first_col:last_col+1]
    
    if add_details:
        rows_cropped_top = first_row
        rows_cropped_bottom = image.shape[0] - last_row - 1
        cols_cropped_left = first_col
        cols_cropped_right = image.shape[1] - last_col - 1
        return (cropped_image, (rows_cropped_top, rows_cropped_bottom, cols_cropped_left, cols_cropped_right))
    else:
        return cropped_image

    return cropped_image

def create20PercentImageFromCSV(csv_file, row, dot_color = "red", background_color=(20,20,20,0), blank_dot_color=(100,100,100), crop=True):
    
    with open(csv_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

            # Skip the first three lines
        for _ in range(row):
            next(csv_reader)
        
        # Read the fourth line
        fourth_line = next(csv_reader)
        fourth_line_without_first_item = fourth_line[1:]
        #print(fourth_line_without_first_item)
        

        fourth_line_without_first_item = [int(float(value.replace(',', '.'))) for value in fourth_line_without_first_item]

        # Reshape the list into a 2D array with a width of 30 pixels
        
        if len(fourth_line_without_first_item) == 2048:        
            sensors_x = 32
            sensors_y = 64
        else:
            sensors_x = 64
            sensors_y = 128
            
        image_array = np.array(fourth_line_without_first_item).reshape(sensors_y, sensors_x)
        
        
        
        
        ############ crop
        if crop:
            (image_array, crop_amount) = crop_image(image_array, True)
            
            (rows_cropped_top, rows_cropped_bottom, cols_cropped_left, cols_cropped_right) = crop_amount
            
        else:
            pass
        
        
        ########## end cropt
        
        
        
        
        (shape_y, shape_x) = image_array.shape
        
        

        width = dimensions.mm2pixel(settings.SENSOR_SIZE * shape_x)  # this is the width of the pressure plate / 2
        height = dimensions.mm2pixel(settings.SENSOR_SIZE * shape_y) 
        image = Image.new("RGBA", (width, height), background_color)

        # Create a drawing object
        draw = ImageDraw.Draw(image)

        
        # Set the radius of the circle
        radius = 10

        # Flatten the array to a 1D array
        flat_data = image_array.flatten()

        # Remove non-positive numbers
        positive_numbers = flat_data[flat_data > 0]

        # Find the largest and smallest positive numbers
        largest_positive = np.max(positive_numbers)
        smallest_positive = np.min(positive_numbers)
        
        
        

        for x in range(0,shape_x):
            for y in range(0,shape_y):
                val = image_array[y][x]

                center_x = dimensions.mm2pixel(settings.SENSOR_SIZE//2) + (x * dimensions.mm2pixel(settings.SENSOR_SIZE)) 
                center_y = dimensions.mm2pixel(settings.SENSOR_SIZE//2) + (y * dimensions.mm2pixel(settings.SENSOR_SIZE)) 

                if val > 0:    
                    radius = int(dimensions.map(val, smallest_positive, largest_positive, 10,30 ))

                    draw.ellipse(
                        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                        fill=dot_color,
                        outline=dot_color,
                    )
                else:
                    radius = 2
                    draw.ellipse(
                        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                        fill=blank_dot_color,
                        outline=None,
                    )                        
                    
    return image





def create20PercentImageFromDataArray(image_array, dot_color = "red", background_color=(20,20,20,0), blank_dot_color=(100,100,100) ):
    (shape_y, shape_x) = image_array.shape

    

    width = dimensions.mm2pixel(settings.SENSOR_SIZE * shape_x)  # this is the width of the pressure plate / 2
    height = dimensions.mm2pixel(settings.SENSOR_SIZE * shape_y) 
    image = Image.new("RGBA", (width, height), background_color)

    # Create a drawing object
    draw = ImageDraw.Draw(image)


    # Set the radius of the circle
    radius = 10

    # Flatten the array to a 1D array
    flat_data = image_array.flatten()

    # Remove non-positive numbers
    positive_numbers = flat_data[flat_data > 0]

    # Find the largest and smallest positive numbers
    largest_positive = np.max(positive_numbers)
    smallest_positive = np.min(positive_numbers)




    for x in range(0,shape_x):
        for y in range(0,shape_y):
            val = image_array[y][x]

            center_x = dimensions.mm2pixel(settings.SENSOR_SIZE//2) + (x * dimensions.mm2pixel(settings.SENSOR_SIZE)) 
            center_y = dimensions.mm2pixel(settings.SENSOR_SIZE//2) + (y * dimensions.mm2pixel(settings.SENSOR_SIZE)) 

            if val > 0:    
                radius = int(dimensions.map(val, smallest_positive, largest_positive, 10,30 ))

                draw.ellipse(
                    [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                    fill=dot_color,
                    outline=dot_color,
                )
            else:
                radius = 2
                draw.ellipse(
                    [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                    fill=blank_dot_color,
                    outline=None,
                )     


    return image




def extractRowFromCSV(csv_file, row, roundData =True):
    
    with open(csv_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

            # Skip the first three lines
        for _ in range(row):
            next(csv_reader)
        
        # Read the fourth line
        fourth_line = next(csv_reader)
        fourth_line_without_first_item = fourth_line[1:]
    
    if roundData:
        fourth_line_without_first_item = [int(float(value.replace(',', '.'))) for value in fourth_line_without_first_item]

    else:    
        fourth_line_without_first_item = [float(value.replace(',', '.')) for value in fourth_line_without_first_item]
    
    return fourth_line_without_first_item




def create20PercentImageFromCSVForMapping(csv_file, row, dot_color = "red", background_color=(20,20,20,0), blank_dot_color=(100,100,100)):
    fourth_line_without_first_item = extractRowFromCSV(csv_file, row)
    
    
    # Reshape the list into a 2D array with a width of 
    if len(fourth_line_without_first_item) == 2048:        
        sensors_x = 32
        sensors_y = 64
    else:
        sensors_x = 64
        sensors_y = 128
        
    original_image_array = np.array(fourth_line_without_first_item).reshape(sensors_y, sensors_x)
    
    
    
    
    ############ crop
    (cropped_image_array, crop_amount) = crop_image(original_image_array, True)
    
    
    image_array = cropped_image_array
    
    ########## end cropt
    image = create20PercentImageFromDataArray(image_array, dot_color, background_color, blank_dot_color)                    
    
    original_image = create20PercentImageFromDataArray(original_image_array, dot_color, background_color, blank_dot_color)                    
                    
    return (original_image, image, crop_amount)