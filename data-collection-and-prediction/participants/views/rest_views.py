from rest_framework import viewsets

from participants.decorators import check_auth_and_superuser
from ..serializers import *
from ..models import *



class ParticipantViewSet(viewsets.ModelViewSet):
    
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    filterset_fields = ['public_id',]


    
class DataProtectionViewSet(viewsets.ModelViewSet):

    queryset = DataProtection.objects.all()
    serializer_class = DataProtectionSerializer

    filterset_fields = ['public_id',]
    

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser
# from drf_yasg.utils import swagger_auto_schema



class UploadedFileViewSet(viewsets.ModelViewSet):
    
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer

    filterset_fields = ['checksum','participant','participant__public_id']
    
  
    @action(detail=False, methods=['post'])
    def create_upload_file(self, request):
        
        greenai_id = request.query_params.get('greenai_id')
        upload_type = request.query_params.get('upload_type')        
        
        participant = Participant.objects.get(public_id=greenai_id)
        
        if participant == None:
            return Response({'error': 'Participant with GAID %s not found' % greenai_id}, status=status.HTTP_400_BAD_REQUEST)
        
        
        uf = UploadedFile.objects.create(participant=participant, upload_type=upload_type)
        serializer =  UploadedFileSerializer(uf)   
                
        return Response(serializer.data, status=status.HTTP_201_CREATED)
            

from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse

from ..models import UploadedFile  # Replace 'your_app' with the actual name of your app
from django.views.decorators.csrf import csrf_exempt


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@check_auth_and_superuser # checks the user token, the secret token as well if the user is an admin
def LinkFileToUploadedFileView(request, file_id):
    # Get the UploadedFile instance by ID


    
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)

    # Get the file from the request
    f =  request.FILES.get('file')
    uploaded_file.file = f

    # Save the changes to the UploadedFile instance
    uploaded_file.save()
    
    checksum = uploaded_file.writeChecksum()

    
    return JsonResponse({'message': 'File linked successfully','checksum':checksum})




@csrf_exempt
@check_auth_and_superuser # checks the user token, the secret token as well if the user is an admin
def LinkFileToDataProtectionView(request, data_protection_id):
    # Get the UploadedFile instance by ID
    
    data_protection = get_object_or_404(DataProtection, id=data_protection_id)

    # Get the file from the request
    f =  request.FILES.get('file')
    data_protection.pdf = f

    # Save the changes to the UploadedFile instance
    data_protection.save()

    checksum = None
    with open(data_protection.pdf.path, 'rb') as file:
        file.seek(0)
        checksum = hashlib.sha256(file.read()).hexdigest()
        file.seek(0)            
        data_protection.checksum=checksum
        data_protection.save()

    return JsonResponse({'message': 'File linked successfully','checksum':checksum})

