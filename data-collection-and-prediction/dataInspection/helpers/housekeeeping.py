from dataInspection.helpers.feetScanner import FootScanner, FootScannerSettings, store_result_to_model
from ..models import *
from participants.models import *
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files import File
import cv2
from PIL import Image
from PIL import Image, ImageEnhance
from io import BytesIO
from django.core.files.base import ContentFile

DEBUG_SCANNER = False #if true, all previously recognised points are deleted and the file is processed again

def enhanceImage(imagePath):
    image = Image.open(imagePath)
    enhancer = ImageEnhance.Contrast(image)
    adjusted_image = enhancer.enhance(2)
    enhancer_brightness = ImageEnhance.Brightness(adjusted_image)
    adjusted_image = enhancer_brightness.enhance(7)
    return adjusted_image

def enhanceFoamPrints(foamPrintAnalysis):
    return
    # left foot
    # if foamPrintAnalysis.leftFoot:        
    #     enhancedLeft = enhanceImage(foamPrintAnalysis.leftFoot.path)
    #     # save it
    #     image_bytes = BytesIO()
    #     enhancedLeft.save(image_bytes, format='JPEG')  # You can choose other formats as needed

    #     # Save the bytes to the ImageField
    #     foamPrintAnalysis.leftFootContrast.save('%s-left-enhanced.jpg'% foamPrintAnalysis.id, ContentFile(image_bytes.getvalue()), save=False)
    #     foamPrintAnalysis.save()
        

    # # left foot
    # if foamPrintAnalysis.rightFoot:        
    #     enhancedLeft = enhanceImage(foamPrintAnalysis.rightFoot.path)
    #     # save it
    #     image_bytes = BytesIO()
    #     enhancedLeft.save(image_bytes, format='JPEG')  # You can choose other formats as needed

    #     # Save the bytes to the ImageField
    #     foamPrintAnalysis.rightFootContrast.save('%s-right-enhanced.jpg'% foamPrintAnalysis.id, ContentFile(image_bytes.getvalue()), save=False)
    #     foamPrintAnalysis.save()
        
        

def createTrainingDataForParticipant(participant, request = None):
    
    # iterate over participants
    
    p = participant
    # first, we need to make sure that we already have a foam print - and exactly one
    
    try:
        foam_print = p.uploads.filter(upload_type = UploadedFile.FOAM_PRINT)[0]
    except:
        print("Participant %s does not have a foam print" % p)
        
        return False
    
    # check if there are already training data samples
    foamPrintAnalysis = None
    
    try:
        foamPrintAnalysis = FoamPrintAnalysis.objects.filter(uploadedFile__participant=p)[0] 
        print("Found the foam print in samples")
    except:
        foamPrintAnalysis = FoamPrintAnalysis.objects.create(uploadedFile=foam_print)
        print("did not find foam print analysis, created a new one")
        
        
    
    # todo, when to do the foam print points?
    # now!
    ###############################
    # only do this if there are no points already
    if foamPrintAnalysis.points.all().count() == 0 or DEBUG_SCANNER: 
        print("we are running the Foam print detection")
        
        foamPrintAnalysis.points.all().delete()
        
        scanner_settings = FootScannerSettings()

        scanner_settings.add_setting('inside',area=300,circularity=0.25,convexity=0.25,inertia=0.25,bgr_threshold=[60,60,60])
        scanner_settings.add_setting('outside',area=500,circularity=0.001,convexity=0.35,inertia=0.35,bgr_threshold=[60,60,150]) 
        
        # Create FootScanner instances
        foot_scanner = FootScanner(scanner_settings)
        
        # check if therer is a scaling factor in the db
        
        scalingFactor = None
        
        if foamPrintAnalysis.scalingFactor != None:
            # there is one
            scalingFactor = foamPrintAnalysis.scalingFactor
            
            print("There is already a scaling factor: %s" % scalingFactor)
        else:
            # there is NONE, try and find it
            print("There is NO scaling factor, we try and get it")
        
            # first see if we can rescale the image
            original_image = cv2.imread(foamPrintAnalysis.uploadedFile.file.path)
            try:
                scalingFactor = foot_scanner.get_scaling_factor_from_marker(original_image,10)
                print("Got scaling factor: %s" % scalingFactor)
            except Exception as e:
                print("Scaling factor could not be determined")
                print("ERROR:" + str(e))
                #raise e
                pass
                # we could not rescale the image, need to inform the user
                if request != None:
                    messages.warning(request, "Kein Skalierungsdreieck gefunden: %s" % foamPrintAnalysis.id)
            else:
                # sclaing worked, save to db
                foamPrintAnalysis.scalingFactor = scalingFactor
                foamPrintAnalysis.save()
        
        
        if scalingFactor != None:        
            
            (result_right, result_left) = foot_scanner.scanImage(foamPrintAnalysis.uploadedFile.file.path, scalingFactor)
            
            if request != None:
                for e in foot_scanner.errors:
                    messages.warning(request, "Fehler %s:" % e)
                    

            flipped_l = foot_scanner.flipResultVertical(result_left)
            
            store_result_to_model(flipped_l, foamPrintAnalysis, True)    
            
                    
            flipped_r = foot_scanner.flipResultVertical(result_right)
            flipped_r = foot_scanner.flipResultHorizontal(flipped_r)

            #flipped_r = foot_scanner.flipResultHorizontal(flipped_r)
            store_result_to_model(flipped_r, foamPrintAnalysis, False)


            _, buffer = cv2.imencode('.jpg', foot_scanner.scaled_image) 
            image_bytes = buffer.tobytes()
            content_file = ContentFile(image_bytes)
            django_file = File(content_file)

            foamPrintAnalysis.scaledImage.save('%s_scaled.jpg' % foamPrintAnalysis.id, django_file)
            foamPrintAnalysis.save()
            
            enhanceFoamPrints(foamPrintAnalysis)
    else:
        print("Threre are already foam print points for FoamPrintAnalysis %s" % foamPrintAnalysis.id)
    
    
    ################################
    
    # iterate over uploaded files, only the pressure plate files, though
    filter_types = [UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_SWAY_R, UploadedFile.PRESSURE_WALK_L, UploadedFile.PRESSURE_WALK_R]
    
    for uploadedFile in p.uploads.filter(upload_type__in = filter_types):
        
        # check if we already have this sample
        if p.trainingData.filter(pressurePlate__uploadedFile=uploadedFile).count() == 0:
            # and now create the actual sample            
            pressurePlateAnalysis = PressurePlateAnalysis.objects.create(uploadedFile=uploadedFile)           
    
            TrainingData.objects.create(
                pressure_type=uploadedFile.upload_type,
                participant = p,
                foamPrint = foamPrintAnalysis,
                pressurePlate = pressurePlateAnalysis
            )
        
        
            
        else:
            pass
            #print("Already pressure plate alignment for UploadedFile %s" % uploadedFile)
        
        
    return True