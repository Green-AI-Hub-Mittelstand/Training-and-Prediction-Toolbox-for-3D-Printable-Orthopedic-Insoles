from rest_framework import  serializers

from dataCollection.generalHelpers.dimensions import mm2pixel
from dataInspection.models import InsoleParameterLeft, InsoleParameterRight
from participants.models import Participant
from ..models import *



class ParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        fields = ['id','public_id','created','shoe_size','weight','height']
        ref_name = "participantSerializerUI"
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Format the created_at field according to your requirements
        
        class_date = timezone.localtime(instance.created)
        representation['created'] = class_date.strftime("%d.%m.%Y %H:%M")
        return representation
    


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'
        


class InsoleParametersProductionSerializer(serializers.ModelSerializer):

    class Meta:
        model = InsoleParametersProduction
        fields = '__all__'
        
        
from django.conf import settings
def scale(_x):
    return _x * settings.SENSOR_SIZE

class PredictedPointSerializer(serializers.ModelSerializer):
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Format the created_at field according to your requirements
        representation['x'] = scale(instance['x'])
        representation['y'] = scale(instance['y'])
        return representation

class PredictedPointLeftSerializer(PredictedPointSerializer):

    class Meta:
        model = PredictedPointLeft
        fields = '__all__'


class PredictedPointRightSerializer(PredictedPointSerializer):

    class Meta:
        model = PredictedPointRight
        fields = '__all__'
        
class InsoleParametersProductionLeft(InsoleParametersProductionSerializer):
    
    points = PredictedPointLeftSerializer(many=True, required=False)
    class Meta:
        model  = InsoleParametersProductionLeft
        fields = '__all__'

class InsoleParametersProductionRight(InsoleParametersProductionSerializer):
    
    points = PredictedPointRightSerializer(many=True, required=False)
    
    class Meta:
        model  = InsoleParametersProductionRight
        fields = '__all__'




from django.utils import timezone

class InsoleSerializer(serializers.Serializer):
    
    leftParameters = InsoleParametersProductionLeft(many=False)
    rightParameters = InsoleParametersProductionRight(many=False)
    #rightParameters = InsoleParametersProductionSerializer(many=False)
    customer = CustomerSerializer(many=False)
    id = serializers.IntegerField()
    created = serializers.DateTimeField()

    """
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Format the created_at field according to your requirements
        
        class_date = timezone.localtime(instance.created)
        representation['created'] = class_date.strftime("%d.%m.%Y %H:%M")
        return representation
    """
    
class ParticipantInsolePointSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
    pointType = serializers.IntegerField()
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Format the created_at field according to your requirements
        representation['x'] = scale(instance['x'])
        representation['y'] = scale(instance['y'])
        return representation


class InsoleParameterLeftSerializer(serializers.ModelSerializer):
    points = ParticipantInsolePointSerializer(many=True)
    class Meta:
        model = InsoleParameterLeft
        fields = '__all__'
        

class InsoleParameterRightSerializer(serializers.ModelSerializer):
    points = ParticipantInsolePointSerializer(many=True)
    class Meta:
        model = InsoleParameterRight
        fields = '__all__'
    



    
class ParticipantInsoleSerializer(serializers.Serializer):
    leftParameters = InsoleParameterLeftSerializer(many=False)
    rightParameters = InsoleParameterRightSerializer(many=False)
    participant = ParticipantSerializer(many=False)
    
    