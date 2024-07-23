from rest_framework import  serializers
from participants.models import *
from rest_framework.parsers import MultiPartParser, FormParser



class ParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        fields = ['created', 'active', 'filled_out_questionnaire', 'signed_dataprotection', 'foam_footprint', 'pressure_plate_done', 'pressure_plate_upload_done', 'participant_compensated', 'desinfected_everything', 'public_id', 'age', 'height', 'weight', 'gender', 'heel_spur_left', 'heel_spur_right', 'leg_shortening_left', 'leg_shortening_right', 'shoe_size', 'pain_points', 'comments_participant', 'comments_experimenter']
        
class DataProtectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataProtection
        fields = [ 'created', 'svg', 'email', 'email_sent', 'name', 'checksum','public_id' ] # pdf
        

class UploadedFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadedFile
        fields = [ 'created', 'participant', 'upload_type'] # file
        