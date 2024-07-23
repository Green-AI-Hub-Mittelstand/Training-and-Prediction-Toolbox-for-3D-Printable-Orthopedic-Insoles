import glob
from ..models import *
from django.conf import settings
import os
from django.core.files import File 
import csv
import tempfile
from pathlib import Path
from django.core.files.storage import default_storage

from django.contrib import messages

def getChecksum(file_stream):
    checksum = None
    file_stream.seek(0)
    checksum = hashlib.sha256(file_stream.read()).hexdigest()
    file_stream.seek(0)            
    return checksum



def createUploadedFile(participant, csv_file, file_type):
    print("Creating file for participant %s, filename %s, type %s" % (participant.id, csv_file, file_type) )
    
    # Create UploadedFile instance
    Path("media\\temp_import_files").mkdir(parents=True, exist_ok=True)

    # Open and read the CSV file
    with open(csv_file, 'rb') as file_data:
        
        lf = tempfile.NamedTemporaryFile(dir=os.path.join('media','temp_import_files'))
        
        
        lf.write(file_data.read())
        
        checksum = getChecksum(lf)
        
        
        # check if we already have this checksum
        already_exist = UploadedFile.objects.filter(checksum=checksum).count()>0
        
        if already_exist:
            print("File %s is already uploaded" % csv_file)
            return
        
        
        
        
        # Assuming the first row contains header information
        file_object = File(lf, name=os.path.basename(csv_file))

        
        uploaded_file = UploadedFile.objects.create(file=file_object, participant=participant, upload_type=file_type )
        #uploaded_file.save()
        print(uploaded_file)
        
        lf.close()
        
        uploaded_file.writeChecksum()
        
        print(f"File '{csv_file}' processed and saved.")
    
    
    pass

def calculate_average(row):
    # Ignore the first column and calculate the average of the remaining columns
    values = [float(value.replace(",",".")) for value in row[1:]]
    return sum(values) / len(values)

def checkFileForFoot(filename):
    try:
        with open(filename, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=';')

            # Skip the first two rows to reach the third row (index 2)
            for _ in range(2):
                next(csv_reader)

            # Read the third row
            third_row = next(csv_reader)

            # Calculate the average
            average = calculate_average(third_row)
            #print(average)
            
            return average > 0.1

            
            
    except Exception as e:
        raise e
        return False


def getLeftRightFeet(csv_dir):
    # iterate over sub dirs
    
    left_feet = []
    right_feet = []
    
    for subdir in glob.glob(os.path.join(csv_dir, "*")):
        #print(subdir)
        
        # in each subdir, look for the left and right foot
        left = None
        
        for f in glob.glob(os.path.join(subdir, "*_L.CSV")):
            if not "_GL_" in f:
                left = f
                if checkFileForFoot(left):
                    left_feet.append(left)
            
        right = None
        
        for f in glob.glob(os.path.join(subdir, "*_R.CSV")):
            if not "_GL_" in f:
                right = f
                if checkFileForFoot(right):
                    right_feet.append(right)
        
        
        #left = list(glob.glob(os.path.join(subdir, "*_L.CSV")))[0]
        #print("%s %s" % (left, checkFileForFoot(left)))
        #print("%s %s" % (right, checkFileForFoot(right)))
        
        
        
        
        
        #print(right)
        
    return (left_feet, right_feet)
    

def importCSVforParticipant(participant):
    #print(settings.CSV_PATH)
    
    # look for the walking files
    walking_dir = os.path.join(settings.CSV_PATH, str(participant.id), "gehen" )
    
    (walking_left, walking_right) = getLeftRightFeet(walking_dir)
    
    
    for lf in walking_left:
        createUploadedFile(participant, lf, UploadedFile.PRESSURE_WALK_L)
    
    for rf in walking_right:
        createUploadedFile(participant, rf, UploadedFile.PRESSURE_WALK_R)
        
    standing_dir = os.path.join(settings.CSV_PATH, str(participant.id), "stehen" )
    
    (standing_left, standing_right) = getLeftRightFeet(standing_dir)
    
    
    for lf in standing_left:
        createUploadedFile(participant, lf, UploadedFile.PRESSURE_SWAY_L)
    
    for rf in standing_right:
        createUploadedFile(participant, rf, UploadedFile.PRESSURE_SWAY_R)
    
    # import the files into the model
    
    #print(walking_dir)