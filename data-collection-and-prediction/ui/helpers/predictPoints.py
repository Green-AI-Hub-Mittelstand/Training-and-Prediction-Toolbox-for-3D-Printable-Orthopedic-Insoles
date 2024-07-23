from ..models import *
from django.core.exceptions import ObjectDoesNotExist
import requests


def _predictPointsFromCSV(csv_path):
    # Send POST request to Flask server with the CSV file
    files = {'file': open(csv_path, 'rb')}
    response = requests.post("http://predictions:5000/predict_points", files=files)

    # Check the response
    if response.status_code == 200:        
        return response.json()
        
    else:
        return []


def predictPoints(insole):
    # left
    leftPoints = _predictPointsFromCSV(insole.pressureFileLeftSway.path)
    rightPoints = _predictPointsFromCSV(insole.pressureFileRightSway.path)
    
    return (leftPoints, rightPoints)
    pass
    

def predictPointsLeft(insole):
    # left
    return _predictPointsFromCSV(insole.pressureFileLeftSway.path)
    
def predictPointsRight(insole):

    return _predictPointsFromCSV(insole.pressureFileRightSway.path)
    
    
def store_poi_left(prediction,poi):
    fp_left = PredictedPointLeft.objects.create(predictions=prediction, x=poi.x,y=poi.y,pointType=poi.role)
            

def store_result_to_model_left(prediction):
    PredictedPointLeft.objects.filter(predictions=prediction).delete()
    for poi in predictPoints():
        store_poi_left(prediction, poi)

def createPredictionforCustomerLeft(insoles, request= None):
    # if points from one Foot get deleted, and the page is refreshed
    # we call predictPoints() which creates new InsoleParameters for both feet
    # to avoid a resulting imbalance (e.g., two right predictions, one left (because of deletion))
    # delete the old right one too, then create the predictions
    prediction_left = PredictionsLeft.objects.create(insoles = insoles)
    #prediction_left = PredictionsLeft.objects.get(id=2) 
    store_result_to_model_left(prediction_left)



def store_poi_right(prediction,poi):
    fp_right = PredictedPointRight.objects.create(predictions=prediction, x=poi.x,y=poi.y,pointType=poi.role)
            
def store_result_to_model_right(prediction):
    
    PredictedPointRight.objects.filter(predictions=prediction).delete()

    for poi in predictPoints():
        store_poi_right(prediction, poi)

def createPredictionforCustomerRight(insoles,request=None):
    # Create new insole parameters and prediction
    prediction_right = PredictionsRight.objects.create(insoles = insoles)
    #prediction_right = PredictionsRight.objects.get(id=1)
    store_result_to_model_right(prediction_right)
