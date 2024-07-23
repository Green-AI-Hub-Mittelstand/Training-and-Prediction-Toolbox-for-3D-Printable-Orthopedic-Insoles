from .models import * 
from ui.models import *
from rest_framework import  serializers



class FoamPrintPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoamPrintPoint
        fields = '__all__'

class PredictionPointLeftSerializer(serializers.ModelSerializer):

    class Meta:
        model = PredictedPointLeft
        fields = '__all__'

class PredictionPointRightSerializer(serializers.ModelSerializer):

    class Meta:
        model = PredictedPointRight
        fields = '__all__'
        
class TrainingDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainingData
        fields = '__all__'
        
        


class PointValidation(serializers.Serializer):
    foundAllPoints = serializers.BooleanField()
    missingPointsNum = serializers.IntegerField()
    identifiedAllPoints = serializers.BooleanField()
    unidentifiedPointsNum = serializers.IntegerField()
    duplicatePointsNum = serializers.IntegerField()    
    duplicatePoints = FoamPrintPointSerializer(many=True)
    ok = serializers.BooleanField()
    missingPointTypes = serializers.ListField(child=serializers.IntegerField())
    
        
class FoamPrintAnalysisSerializer(serializers.ModelSerializer):
    pointsRightComplete = PointValidation(many=False, read_only=True)
    pointsLeftComplete = PointValidation(many=False, read_only=True)
    
    
    
    class Meta:
        model = FoamPrintAnalysis
        fields = ["id","uploadedFile","leftFoot","rightFoot","scaledImage","scalingFactor","pointsRightComplete","pointsLeftComplete"]
        
        