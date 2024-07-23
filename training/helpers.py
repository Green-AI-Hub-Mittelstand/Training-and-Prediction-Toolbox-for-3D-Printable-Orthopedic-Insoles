import os, requests, zipfile, math, json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from secretToken import TOKEN

def download_and_extract_zip(url, target, TOKEN):
    os.makedirs(target,  exist_ok=True)
    
    headers = {'ReadOnlySecret': TOKEN}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Save the zip file
        zip_file_path = os.path.join(target, 'data_orig.zip')
        with open(zip_file_path, 'wb') as f:
            f.write(response.content)
        
        # Unzip the file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(target)
        
        # Delete the zip file
        os.remove(zip_file_path)
        
    else:
        print(f"Failed to download. Status code: {response.status_code} - {url}")

def downloadParticipant(participant_id, add_video=False, _base_url = "https://green-ai.umtl.dfki.dev/downloadTrainingData/", _data_path="data"):
    BASE_URL = _base_url
    DATA_PATH = os.path.join(_data_path)

    url = BASE_URL + str(participant_id)

    if add_video:
        url+="?add_video=1"

    download_and_extract_zip(url,DATA_PATH, TOKEN )


def map(value, in_min, in_max, out_min, out_max):
    # Map the input value from the input range to the output range
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def renderMappedTrainingData(mappedPoints, csvRow, scale = 1, predictedPoints=[], plotPointNumbers = False):
    """Renders an image of a data_orig sample. If provided, also renders the predicted points.

    Args:
        mappedPoints (list): an Array of Objects in the form of {"points":[x,y], "pointType":int}
        csvRow (list): Flat array of the pressure values, 32x64
        scale (int, optional): Scales the image. Defaults to 1.
        predictedPoints (list, optional): If supplied, also plots the predicted points. Defaults to [].
        plotPointNumbers (bool, optional): If true, adds labels to both, the predicted and the ground truth points  . Defaults to False.

    Returns:
        PIL.Image: The resulting image.
    """
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
    
    # Set the base scale of the label
    baseFontSize = .75


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
                radius = int(map(val, smallest_positive, largest_positive, pressurePointRadiusMin,pressurePointRadiusMax ))

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

    font = ImageFont.truetype("arial.ttf",int(baseFontSize*scale))


    # now draw the ground points
    for point in mappedPoints:
        
        (x,y) = point['points']
        pType = point['pointType']

        radius = markedPointRadius
        
        (x,y) = (x*scale, y*scale)
        
        color = (0,255,0)
        colorOffset = 150
        
        (c1, c2, c3) = color        
        fontColor = (max(0,c1-colorOffset), max(0,c2-colorOffset), max(0,c3-colorOffset))

        draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=color)      
        
        if plotPointNumbers:
            draw.text((x-int(1*scale), y-int(1*scale)), str(pType), fill=fontColor, font=font)
        
              
        
    # now draw the predictedPoints
    for point in predictedPoints:
        
        (x,y) = point['points']
        pType = point['pointType']

        radius = markedPointRadius
        
        (x,y) = (x*scale, y*scale)
        
        color = (0,0,255)
        colorOffset = 150
        
        (c1, c2, c3) = color
        
        fontColor = (max(0,c1-colorOffset), max(0,c2-colorOffset), max(0,c3-colorOffset))

        draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=color)     
        
        if plotPointNumbers:
            draw.text((x+int(.3*scale), y+int(.3*scale)), str(pType), fill=fontColor, font=font)
   
    return image

# Normalize the values of an array (between 0 and the maximum value of the given array)
def normalize_array(array):
    m = max(array)
    return [i / m for i in array]

# Normalizes the pressure data of a given data_frame
def normalize_df(df):
    ''' Normalizes the 'input_features' of a given data frame and returns the result
    '''
    df['input_features'] = df['input_features'].apply(normalize_array)
    return df


def walkingLine(df, participantID, left_or_right):
    ''' Calulates and returns an array containing the center of pressure for all frames of the given dataframe
        Args:
            df (dataFrame): The dataframe to use
            participantID (String): A String (!) containing the wanted id.
            left_or_right (String): A string that is either "left" or right", 
        Returns:
            List: A list containing all centers of mass for each sample
    '''
    line = []
    # Get the needed 'subframe', with fitting participant number and foot
    subFrame = df.loc[(df["participant_number"] == participantID) & (df["left_or_right"] == left_or_right)]
    
    # Loop through all samples
    for sample in range(len(subFrame)): 
        xmean = 0
        ymean = 0
        totalMass = 0
        # Add up all weighted points in a loop and divide afterwards
        # (Dimensions are: width = 32, height = 64)
        for x in range(32):
            for y in range(64):
                index = y * 32 + x
                mass = subFrame['input_features'].iloc[sample][index]
            
                xmean += mass * x
                ymean += mass * y
                totalMass += mass
        if totalMass > 0:
            xmean /= totalMass
            ymean /= totalMass
            line.append((xmean, ymean))
    return line

def getNeighbourhood(sample, width, height, point, n):
    """ Get the n x n neighbourhood of a point from a sample. (Please note that this function wont return a square-list if some needed indices are out of bounds)
        Args:
                sample (list): The w x h list from which we get the neighbourhood
                width (int): Width of the list
                height (int): Height of the list
                point (double, double): The point form which we get the neighbourhood
                n (int, odd): An odd int for the size if the square
    """
    # Get middlepoint:
    (xm, ym) = point
    xm = int(round(xm)) # Built-In round function
    ym = int(round(ym))

    neighbourhood = []

    c = int((n-1)/2)
    for y in range(ym - c, ym + c + 1):
        for x in range(xm - c, xm + c + 1):
            # Check if point is in array
            if not (min(x,y) < 0 or x >= width or y >= height):
                neighbourhood.append(sample[x + y * width])
            else:
                neighbourhood.append(0)
    return neighbourhood
    
    

def getNeighbourhoodFromDf(df, sampleID, left_or_right, pointType, n):
    """ Returns a list of a n x n Neighbourhood of a certain point. If the neighbourhood crosses the boundary, outside values are padded with 0s
         Args:
                df (dataFrame): The dataframe to use
                sampleID (String): A String (!) containing the id for the wanted sample.
                left_or_right (String): A string that is either "left" or right", 
                pointType (String): A String of the pointType ("0" to "21"),
                n (int): The size of the neighbourhood
        Returns:
                List: A 1-D list of the n x n neighbourhood
        
    """
    # Get the sample:
    row = df.loc[df["sample_number"] == sampleID]
    point = row["pointType_"+pointType][0]

    # Get the neighbourhood from around point:
    return getNeighbourhood(row["input_features"][0], 32, 64, point, n)

def centerOfMass(pressure_data):
    '''
        Returns center of mass for a 32 x 64 list as a tuple. (Breaks if total mass is 0!!)
    '''
    xmean = 0
    ymean = 0
    totalMass = 0
    for x in range(32):
        for y in range(64):
            index = y * 32 + x
            mass = pressure_data[index]        
            
            xmean += mass * x
            ymean += mass * y
            totalMass += mass
    # if totalMass > 0:
    xmean /= totalMass
    ymean /= totalMass
    return (xmean, ymean)
    # else:
    #     return (15.5, 31.5)


def distanceToSchnittachse(df, participantID, left_or_right, numOfSegments):
    """ Returns a list of length numOfSegments, each filled with a list of dicts of the form { "com":{ "x":_, "y":_, "force":_}, "length":_ }. length will be negative if the com is to the left of the axis.
         Args:
                df (dataFrame): The dataframe to use
                participantID (String): A String (!) containing the id of the participant.
                left_or_right (String): A string that is either "left" or right",
                numOfSegments (int): How many segment will be split into. Note that if numOfSegments isn't a divider of the total number of samples, the sublists won't all be equal in size
        Returns:
                List: A list of lists of dicts in the specified format
        
    """
    # Relevant subFrame:
    subFrame = df.loc[(df["participant_number"] == participantID) & (df["left_or_right"] == left_or_right)]
    size = len(subFrame)

    result = []
    
    for step in range(numOfSegments):

        segmentResult = []
        
        # Go from first index to first index of next Segment - 1:
        for i in range( int(size * step/numOfSegments),  int(size * (step + 1)/numOfSegments)):
            # Dataframe of current timestamp:
            data = subFrame.iloc[i]

            # Create Dict to store result:
            intermediateResult = dict()
            
            # Construct Schnittachse (of form a + lambda * u, lambda in R):
            # Relevant pointIDs are: (21, "SCHNITTACHSE"), (20, "HINTERSTER_PUNKT")
            # a = Schnittachse:
            (ax, ay) = data["pointType_21"]
            # u = Hinterster Punkt - Schnittachse:
            (ux, uy) = data["pointType_20"]
            ux -= ax
            uy -= ay
            # Get Center of mass for current timestamp:
            (comX, comY) = centerOfMass(data["input_features"])
            mass = sum(data["input_features"])
            # Store com in intermediate Result:
            intermediateResult["com"] = {"x": comX, "y": comY, "force": mass}

            # e: u * (x - com) = 0
            # Lotfußpunkt at lamda = u * (p - a) / (u^2)  (constructing a temporary plane through p and solving for lambda)
            lam = -(ux * (ax - comX) + uy * (ay - comY)) / (ux * ux + uy * uy)
            
            # Get nearest Point to Com
            lotX = lam * ux + ax
            lotY = lam * uy + ay
            
            # Compute distance
            dist = np.sqrt((lotX - comX)**2 + (lotY - comY)**2)

            # Check if com is on left or right side by using the distance Vector to the lot
            if (comX - lotX) < 0:
                # on left side, since vector points in neg X dir.
                dist *= -1
            
            # Store result: (TODO: Sign of length depending on side):
            intermediateResult["length"] = dist

            # Store in SegmentResults
            segmentResult.append(intermediateResult)

        # Store in final result:
        result.append(segmentResult)

    return result
