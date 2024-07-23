from rest_framework import  serializers
from .models import *
from rest_framework.parsers import MultiPartParser, FormParser
from dataInspection.models import InsoleParameters, InsoleParameterLeft, InsoleParameterRight, TrainingData

class TrainingDataML(serializers.ModelSerializer):
    
    class Meta:
        model = TrainingData
        fields = ['id','pressure_type', 'participant','fit_quality','foot']

class InsoleParametersMlLeft(serializers.ModelSerializer):
    
    
    class Meta:
        model = InsoleParameterLeft
        fields = '__all__'

class InsoleParametersMlRight(serializers.ModelSerializer):
    
    class Meta:
        model = InsoleParameterRight
        fields = '__all__'

class AllowCreatedSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # Extract the datetime value from the validated data
        created = validated_data.pop('created', None)

        # Create an instance without setting the datetime field
        instance = self.Meta.model.objects.create(**validated_data)

        # Set the datetime field if a value is provided
        if created is not None:
            instance.created = created
            instance.save()

        return instance

class ParticipantSerializerML(serializers.ModelSerializer):
    
    
    class Meta:
        model = Participant
        fields = ['public_id','created','age','height','weight','gender','heel_spur_left','heel_spur_right','leg_shortening_left','leg_shortening_right','shoe_size','comments_participant','comments_experimenter','pain_points']

class ParticipantSerializer(AllowCreatedSerializer):

    class Meta:
        model = Participant
        fields = '__all__'
        
class DataProtectionSerializer(AllowCreatedSerializer):

    class Meta:
        model = DataProtection
        fields = '__all__'
        

class UploadedFileSerializer(AllowCreatedSerializer):

    class Meta:
        model = UploadedFile
        fields = '__all__'
        #parser_classes = (MultiPartParser, FormParser)