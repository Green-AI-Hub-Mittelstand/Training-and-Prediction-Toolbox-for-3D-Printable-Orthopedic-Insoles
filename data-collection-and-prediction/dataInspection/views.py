from django.shortcuts import render
from dataInspection.forms import InsoleParameterFormLeft, InsoleParameterFormRight
from dataInspection.helpers.housekeeeping import createTrainingDataForParticipant
from dataInspection.helpers.pois import FOAM_POINT_CHOICES, FOAM_POINT_CHOICES_SHORT
from dataInspection.models import *
from participants.decorators import admin_required
from participants.models import Participant
from django.shortcuts import get_object_or_404
import json
from .serializers import *
from rest_framework import viewsets

# Create your views here.


def impressum(request):
    return render(request, 'imprint.html')

def datenschutz(request):
    return render(request, 'dataprotection.html')

@admin_required
def inspectParticipant(request, participant_id):

    participant = get_object_or_404(Participant, pk=participant_id)

    left_points = []
    right_points = []
    
    print(participant)

        
    fp = participant.analyzedFoamPrint

    if fp:
        for p in fp.pointsLeft:
            s = FoamPrintPointSerializer(p)
            left_points.append(s.data)

        for p in fp.pointsRight:
            s = FoamPrintPointSerializer(p)
            right_points.append(s.data)

    foamPoints = json.dumps(FOAM_POINT_CHOICES)
    foamPointsShort = json.dumps(FOAM_POINT_CHOICES_SHORT)    
    

    

    return render(request, "inspectParticipant.html", {"participant":participant, "leftPoints":json.dumps(left_points), "rightPoints":json.dumps(right_points), "foamPoints":foamPoints,"foamPointsShort":foamPointsShort})

@admin_required
def inspectVideos(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)

        
    fp = participant.analyzedFoamPrint

    
    foamPoints = json.dumps(FOAM_POINT_CHOICES)
    
    
    
    
    foamPointsShort = json.dumps(FOAM_POINT_CHOICES_SHORT)    
    return render(request, "inspectVideos.html", {"participant":participant,  "foamPoints":foamPoints, "foamPointsShort":foamPointsShort,  })

from django.contrib import messages

@admin_required
def inspectInsole(request, participant_id):

    participant = get_object_or_404(Participant, pk=participant_id)

    left_points = []
    right_points = []
    
    print(participant)

        
    fp = participant.analyzedFoamPrint

    if fp:
        for p in fp.pointsLeft:
            s = FoamPrintPointSerializer(p)
            left_points.append(s.data)

        for p in fp.pointsRight:
            s = FoamPrintPointSerializer(p)
            right_points.append(s.data)

    foamPoints = json.dumps(FOAM_POINT_CHOICES)
    
    
    parametersLeft = None
    try:
        parametersLeft = InsoleParameterLeft.objects.get(participant=participant)
    except:
        parametersLeft = InsoleParameterLeft.objects.create(participant=participant)
    
    parametersRight = None
    try:
        parametersRight = InsoleParameterRight.objects.get(participant=participant)
    except:
        parametersRight = InsoleParameterRight.objects.create(participant=participant)
        
    assert parametersLeft != None
    assert parametersRight != None
    
    insoleLeftForm = InsoleParameterFormLeft(instance=parametersLeft, prefix="left")
    insoleRightForm = InsoleParameterFormRight(instance=parametersRight, prefix="right")


    if request.method == 'POST':
        insoleLeftForm = InsoleParameterFormLeft(request.POST, prefix='left', instance = parametersLeft)
        insoleRightForm = InsoleParameterFormRight(request.POST, prefix='right', instance = parametersRight)

        if insoleLeftForm.is_valid():
            # Save data for the first instance
            parametersLeft = insoleLeftForm.save()
            messages.info(request, "Linke Parameter gespeichert ")
            
        else:
            messages.error(request, "Linke Parameter konnten nicht gespeichert werden")
            print(insoleLeftForm.errors) 
            
        if  insoleRightForm.is_valid():
            # Save data for the second instance
            parametersRight = insoleRightForm.save()
            messages.info(request, "Rechte Parameter gespeichert ")
            
        else:
            messages.error(request, "Rechte Parameter konnten nicht gespeichert werden")
            print(insoleRightForm.errors)
 
 
    
    foamPointsShort = json.dumps(FOAM_POINT_CHOICES_SHORT)    
    return render(request, "inspectInsole.html", {"participant":participant, "leftPoints":json.dumps(left_points), "rightPoints":json.dumps(right_points), "foamPoints":foamPoints, "foamPointsShort":foamPointsShort, "insoleLeftForm":insoleLeftForm,"insoleRightForm":insoleRightForm })



class FoamPrintPointViewSet(viewsets.ModelViewSet):

    queryset = FoamPrintPoint.objects.all()
    serializer_class = FoamPrintPointSerializer

    filterset_fields = ['foot','foamPrintAnalysis','pointType']
    
    

class TrainingDataViewSet(viewsets.ModelViewSet):

    queryset = TrainingData.objects.all()
    serializer_class = TrainingDataSerializer
    
class FoamPrintAnalysisViewSet(viewsets.ModelViewSet):

    queryset = FoamPrintAnalysis.objects.all()
    serializer_class = FoamPrintAnalysisSerializer