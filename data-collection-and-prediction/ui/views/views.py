from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse

from dataCollection.generalHelpers.dimensions import mm2pixel
from participants.views.preview_views import getMappedTrainingData
from ui.serializers.serializers import CustomerSerializer, InsoleSerializer, ParticipantInsoleSerializer, ParticipantSerializer, InsoleParametersProductionLeft as InsoleParametersProductionLeftSerializer, InsoleParametersProductionRight as InsoleParametersProductionRightSerializer


from participants.models import Participant



from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from django.conf import settings

import time

from ..models import *


from django.forms import ModelForm, Form
from django import forms
from ..forms.widgets import CoordinateInput

from django.contrib.admin.views.decorators import staff_member_required


from django.shortcuts import get_object_or_404
import json
from dataInspection.serializers import *
from dataInspection.helpers.pois import FOAM_POINT_CHOICES, FOAM_POINT_CHOICES_SHORT

from participants.helpers.render import create20PercentImageFromCSV
from io import BytesIO

from ..helpers import predictPoints, predictParameters

from rest_framework import viewsets

from django.contrib import messages



# Create your views here.


def landingUI(request):
    
    customers = Customer.objects.all()
    
    context = {
        'customers':customers
    }
    
    return render(request, "landingUi.html", context)


def customer(request, id):
    
    customer = Customer.objects.get(id=id)
    
    context = {
        'customer': customer,
        'insoles' : Insole.objects.filter(customer=customer).all()
    }
    
    return render(request, "customer.html", context)
    

class CustomerForm(ModelForm):
    """Form definition for Customer."""

    class Meta:
        """Meta definition for Customerform."""

        model = Customer
        fields = ('first_name', 'last_name', 'leg_shortening_left','leg_shortening_right','heel_spur_left','heel_spur_right','comments_customer')

        widgets = {
            'pain_points' : CoordinateInput(attrs={'id': 'pain_points','image_url':'feet-new.jpg','width':600,'height':659})
        }
        
        
def redirect_to_customer_page(request, id):
    user_specific_url = reverse('customer', kwargs={'id': id})
    return redirect(user_specific_url)

from django.utils.translation import activate

def new_customer(request):
    
    activate("de")
    request.session['django_language'] = "de"
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            new_customer = form.save() 
            new_customer_id = new_customer.id
            return redirect_to_customer_page(request, new_customer_id)
    else:
        form = CustomerForm()
    
    return render(request,'customer_new.html',{'form': form})

class InsoleForm(ModelForm):
    """Form definition for Customer."""

    class Meta:
        """Meta definition for InsoleForm."""

        model = Insole
        
        fields = ('pressureFileLeftWalk', 'pressureFileRightWalk','pressureFileLeftSway', 'pressureFileRightSway')

class InsoleParametersProductionFormLeft(ModelForm):

    class Meta:
        """Meta definition for InsoleParameterProductionLeftForm."""

        model = InsoleParametersProductionLeft
        
        fields = '__all__'
        exclude = ('insole',)

class InsoleParametersProductionFormRight(ModelForm):

    class Meta:
        """Meta definition for InsoleParameterProductionRightForm."""

        model = InsoleParametersProductionRight
        
        fields = '__all__'
        exclude = ('insole',)

def new_customer_insoles(request,id):

    if request.method == 'POST':
        form = InsoleForm(request.POST, request.FILES)
        if form.is_valid():
            insole = form.save(commit=False)   
            insole.customer = Customer.objects.get(id=id)
            insole.save()
            return redirect('customer', id=id)
               
    else:
        form = InsoleForm()

      
    context = {
        'customer': Customer.objects.get(id=id),
        'form': form,
        'participants':Participant.objects.all().order_by("-id")
    }
    
    return render(request, "customer_insoles_new.html",context)



def copyInsoleParamterData(target, source):
    target.laenge_der_einlage                       = source.laenge_der_einlage                      
    target.breit_der_einlage_im_vorfussbereich      = source.breit_der_einlage_im_vorfussbereich     
    target.breite_der_einlage_im_rueckfussbereich   = source.breite_der_einlage_im_rueckfussbereich  
    target.mfk_1_entlasten                          = source.mfk_1_entlasten                         
    target.mfk_2_entlasten                          = source.mfk_2_entlasten                         
    target.mfk_3_entlasten                          = source.mfk_3_entlasten                         
    target.mfk_4_entlasten                          = source.mfk_4_entlasten                         
    target.mfk_5_entlasten                          = source.mfk_5_entlasten                         
    target.zehe_1_entlasten                         = source.zehe_1_entlasten                        
    target.zehe_2_entlasten                         = source.zehe_2_entlasten                        
    target.zehe_3_entlasten                         = source.zehe_3_entlasten                        
    target.zehe_4_entlasten                         = source.zehe_4_entlasten                        
    target.zehe_5_entlasten                         = source.zehe_5_entlasten                        
    target.pelotten_hoehe                           = source.pelotten_hoehe                          
    target.pelotten_form                            = source.pelotten_form                           
    target.laengsgewoelbe_hoehe                     = source.laengsgewoelbe_hoehe                    
    target.basis_5_entlasten                        = source.basis_5_entlasten                       
    target.fersensporn                              = source.fersensporn                             
    target.aussenrand_anheben                       = source.aussenrand_anheben                      
    target.innenrand_anheben                        = source.innenrand_anheben                       
    target.verkuerzungsausgleich                    = source.verkuerzungsausgleich                   
    
    


def new_customer_insoles_copy_from_participant(request,id):
    if request.method == 'POST':
        participant_id = request.POST['participant']
      
        # generate an insole
      
        participant = Participant.objects.get(pk=participant_id)
      
        
        insole = Insole.objects.create(customer_id=id, 
                                       pressureFileLeftWalk=participant.left_walk.file,
                                       pressureFileRightWalk=participant.right_walk.file,
                                       pressureFileLeftSway=participant.left_sway.file,
                                       pressureFileRightSway=participant.right_sway.file)
      
        ### create left predictions
        # insole parameters
      
        insoleParamsLeft = InsoleParametersProductionLeft()
        insoleParamsLeft.insole = insole
        copyInsoleParamterData(insoleParamsLeft, participant.insoleparameterleft)
        insoleParamsLeft.save()
      
        insoleParamsRight = InsoleParametersProductionRight()
        insoleParamsRight.insole = insole
        copyInsoleParamterData(insoleParamsRight, participant.insoleparameterright)
        insoleParamsRight.save()
      
      
      
        # now points for left and right
        tdLeft = participant.trainingData.filter(pressure_type=UploadedFile.PRESSURE_SWAY_L).first()
        tdRight = participant.trainingData.filter(pressure_type=UploadedFile.PRESSURE_SWAY_R).first()
      
        (mappedPointsLeft, csvRowLeft) = getMappedTrainingData(tdLeft.id)
        (mappedPointsRight, csvRowRight) = getMappedTrainingData(tdRight.id)
      
        for pointLeft  in mappedPointsLeft:
            (x,y) = pointLeft['points']
            pointType = pointLeft['pointType']
          
            PredictedPointLeft.objects.create(insole=insole, x=x, y=y, pointType=pointType)
      
        for pointRight in mappedPointsRight:
            (x,y) = pointRight['points']
            pointType = pointRight['pointType']
          
            PredictedPointRight.objects.create(insole=insole, x=x, y=y, pointType=pointType)
      
      
        #return HttpResponse("partiticant %s " % participant_id)
        return redirect('customer', id=id)
     
    else:
        participants = Participant.objects.all().order_by('public_id')
        
        p_new = []
        
        for p in participants:
            try:
                x = p.insoleparameterleft
            except:
                pass
            else:
                p_new.append(p)
        
        return render(request, "copy_from_participant.html", {'participants':p_new})




def point_predictor_status(request, insole_id):
    insole = Insole.objects.get(id = insole_id)
    return render(request, "predict_points_status.html", {"insole":insole})
    
    
    pass

import time



def predict_params_view(request, insole_id):
    # figure out the csvs, to the request
    
    insole = Insole.objects.get(id = insole_id)
    
    (leftParams, rightParams) = predictParameters.predictParams(insole)
    
    print(leftParams)
    
    ## store the params
    
    try:
        insole.leftParameters.delete()
        
    except:
        pass
    
    try:
        insole.rightParameters.delete()
    except:
        pass
    
    leftData = InsoleParametersProductionRightSerializer(data=leftParams['predictions'])
    if leftData.is_valid():
        
        x = leftData.save()
        x.insole = insole
        x.save()
        
    else:
        return HttpResponse(str(leftData.errors))
        
    
    rightData = InsoleParametersProductionLeftSerializer(data=rightParams['predictions'])
    if rightData.is_valid():
        
        x = rightData.save()
        x.insole = insole
        x.save()
        
    else:
        return HttpResponse(str(rightData.errors))
        
    
    
    return HttpResponse("Done")

def predict_points_view(request, insole_id):
    # figure out the csvs, to the request
    
    insole = Insole.objects.get(id = insole_id)
    
    (leftPoints, rightPoints) = predictPoints.predictPoints(insole)
    print(leftPoints)
    
    PredictedPointLeft.objects.filter(insole=insole).delete()
    for lp in leftPoints['predictions']:
        print(lp)
        [x,y]= lp['points']
        PredictedPointLeft.objects.create(insole=insole, x=x, y=y, pointType=lp['pointType'])
    
    PredictedPointRight.objects.filter(insole=insole).delete()
    for rp in rightPoints['predictions']:
        [x,y]= rp['points']
        PredictedPointRight.objects.create(insole=insole, x=x, y=y, pointType=rp['pointType'])
    
    return HttpResponse("ok")
    pass

def predict_points_view_generator(request, insole_id):
    # figure out the csvs, to the request
    
    _insole = Insole.objects.get(id = insole_id)
    
    def generate(insole):
        
        yield "data: 0\n\n"
        total  = 22 *2
        
        counter = 0
        
        leftPoints = predictPoints.predictPointsLeft(insole)
        PredictedPointLeft.objects.filter(insole=insole).delete()
        for lp in leftPoints['predictions']:
            print(lp)
            [x,y]= lp['points']
            PredictedPointLeft.objects.create(insole=insole, x=x, y=y, pointType=lp['pointType'])
            counter+=1
            
            
            yield "data: %s\n\n" % str(float(counter/total))
        
        
        rightPoints = predictPoints.predictPointsRight(insole)
        
        
        PredictedPointRight.objects.filter(insole=insole).delete()
        for rp in rightPoints['predictions']:
            [x,y]= rp['points']
            PredictedPointRight.objects.create(insole=insole, x=x, y=y, pointType=rp['pointType'])
            
            counter+=1
            yield "data: 1\n\n"
            #yield str(float(counter/total))
        
        yield str(1)
    
    response = StreamingHttpResponse(generate(_insole), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    #response['Connection'] = 'keep-alive'

    return response



def param_editor(request, insole_id):
    insole = Insole.objects.get(id = insole_id)
    
    
    paramsAvailable = True
    
    try:
        x =insole.leftParameters
        x = insole.rightParameters
    except:
        paramsAvailable = False
        
    if not paramsAvailable:
        # redirect to point predictor
        return redirect("param_predictor_status",insole_id)
    
    
    if request.method == 'POST':
        insoleLeftForm = InsoleParametersProductionFormLeft(request.POST, prefix='left', instance = insole.leftParameters)
        insoleRightForm = InsoleParametersProductionFormRight(request.POST, prefix='right', instance = insole.rightParameters)

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
 
    else:
        
        
        
        
        insoleLeftForm = InsoleParametersProductionFormLeft(instance=insole.leftParameters, prefix="left")
        insoleRightForm = InsoleParametersProductionFormRight(instance=insole.rightParameters, prefix="right")
    
    return render(request, "param_editor.html", {
        "insole":insole,
        "insoleParametersFormLeft":insoleLeftForm,
        "insoleParametersFormRight":insoleRightForm,
        
    })
        



def param_predictor_status(request, insole_id):
    insole = Insole.objects.get(id = insole_id)
    return render(request, "predict_params_status.html", {"insole":insole})
    return HttpResponse("predict points")
    
    pass
    

def point_editor(request, insole_id):
    # figure out the csvs, to the request
    insole = Insole.objects.get(id = insole_id)
    
    # check if this insole has points yet
    if insole.leftPoints.all().count() == 0:
        # redirect to point predictor
        return redirect("point_predictor_status",insole_id)
    
    left_points = []
    right_points= []
    
    fp_left = insole.leftPoints.all()
    fp_right = insole.rightPoints.all()
    
    if fp_right:
        for p in fp_right:
            s = PredictionPointRightSerializer(p)
            
            # scale the points
            
            point = {
                "x":mm2pixel(s.data["x"] * settings.SENSOR_SIZE),
                "y":mm2pixel(s.data["y"] * settings.SENSOR_SIZE),
                "pointType":s.data['pointType'],
                "id":s.data['id'],
                "scale":  s.data["x"] / mm2pixel(s.data["x"] * settings.SENSOR_SIZE)
            }
            
            #print(s.data)
            right_points.append(point)
    if fp_left:
        for p in fp_left:
            s = PredictionPointLeftSerializer(p)
            
            point = {
                "x":mm2pixel(s.data["x"] * settings.SENSOR_SIZE),
                "y":mm2pixel(s.data["y"] * settings.SENSOR_SIZE),
                "x_orig":s.data["x"],
                "pointType":s.data['pointType'],
                "id":s.data['id'],
                "scale":  s.data["x"] / mm2pixel(s.data["x"] * settings.SENSOR_SIZE)
            }
            
            
            left_points.append(point)
    
   
    foamPoints = json.dumps(FOAM_POINT_CHOICES)
    foamPointsShort = json.dumps(FOAM_POINT_CHOICES_SHORT)
    
    
    context = {
        'customer': insole.customer,
        'insole': insole,
        'foamPoints': foamPoints,
        'foamPointsShort':foamPointsShort,
        #'insoleParametersFormLeft':insoleLeftForm,
        #'insoleParametersFormRight':insoleRightForm,
        'leftPoints':json.dumps(left_points),
        'rightPoints':json.dumps(right_points),    
    }
    
    return render(request, "point_editor.html",context)
    pass



def render20percentNativeCSVUI(request, insole_id, foot, row=2):
    uploaded_file = get_object_or_404(Insole, id=insole_id)
    color = request.GET.get('color',"red")
    crop = request.GET.get('crop',"true") == "true"
    print("############### %s" % crop)
    
    insole = get_object_or_404(Insole, pk=insole_id)
    
    # get the csv file
    csv_file = None
    
    if foot == "left":
        csv_file = insole.pressureFileLeftSway.path
    else:
        csv_file = insole.pressureFileRightSway.path
    
    image = create20PercentImageFromCSV(csv_file, row, color, crop=crop)

    # Save the image to a BytesIO object
    image_io = BytesIO()
    image.save(image_io, format="PNG")
    image_io.seek(0)

    image_data = image_io.read()

    # Create an HTTP response with the image
    response = HttpResponse(image_data, content_type="image/png")


    response['Content-Disposition'] = "inline; filename=%s.png" % (uploaded_file.id,)
    response['X-Content-Type-Options'] = 'nosniff'  # Add this header to prevent MIME type sniffing

    return response

class PredictedPointLeftViewSet(viewsets.ModelViewSet):

    queryset = PredictedPointLeft.objects.all()
    serializer_class = PredictionPointLeftSerializer

    filterset_fields = ['pointType']
    
class PredictedPointRightViewSet(viewsets.ModelViewSet):

    queryset = PredictedPointRight.objects.all()
    serializer_class = PredictionPointRightSerializer

    filterset_fields = ['pointType']    
    
    
    
class CustomerViewSet(viewsets.ReadOnlyModelViewSet ):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    
class InsoleViewSet(viewsets.ReadOnlyModelViewSet ):
    
    

    queryset = Insole.objects.all()
    serializer_class = InsoleSerializer
    
    filterset_fields = ['customer']
    
    
    @swagger_auto_schema(
        method='get',
        responses={200: ParticipantInsoleSerializer(many=False)},
        operation_description="Returns the insole for fusion",)      
    @action(detail=True, methods=['get'])
    def insole(self, request, pk=None):
        
        insole = get_object_or_404(Insole, id=pk)
        
        paramsLeft = insole.leftParameters
        paramsRight = insole.rightParameters
        
        paramsLeft.points = []
        paramsRight.points = []
        
        """
        tdLeft = participant.trainingData.filter(pressure_type=UploadedFile.PRESSURE_SWAY_L).first()
        tdRight = participant.trainingData.filter(pressure_type=UploadedFile.PRESSURE_SWAY_R).first()
        
        (mappedPointsLeft, csvRowLeft) = getMappedTrainingData(tdLeft.id)
        (mappedPointsRight, csvRowRight) = getMappedTrainingData(tdRight.id)
        """
        
        for pointLeft  in insole.leftPoints.all():
            
            
            paramsLeft.points.append({
                "x":pointLeft.x,
                "y":pointLeft.y,
                "pointType":pointLeft.pointType
            })
            
            
        
        for pointRight in insole.rightPoints.all():
            
            paramsRight.points.append({
                "x":pointRight.x,
                "y":pointRight.y,
                "pointType":pointRight.pointType
            })
            
        
        # generate the response
        data = {
            'leftParameters':paramsLeft,
            'rightParameters':paramsRight,
            'customer':insole.customer,
            'created':insole.created,
            'id':insole.id
            #'participant':participant
        }
        
        s = InsoleSerializer(data)
        
        return Response(s.data)
        
        return Response({'status': 'password set'})
    




class ParticipantViewSet(viewsets.ReadOnlyModelViewSet ):
    
    queryset = Participant.objects.exclude(insoleparameterleft__isnull=True,insoleparameterright__isnull=True)
    serializer_class = ParticipantSerializer
    
    @swagger_auto_schema(
        method='get',
        responses={200: ParticipantInsoleSerializer(many=False)},
        operation_description="Returns the insole to this participant",)      
    @action(detail=True, methods=['get'])
    def insole(self, request, pk=None):
        
        participant = get_object_or_404(Participant, public_id=pk)
        
        paramsLeft = participant.insoleparameterleft
        paramsRight = participant.insoleparameterright
        
        paramsLeft.points = []
        paramsRight.points = []
        
        tdLeft = participant.trainingData.filter(pressure_type=UploadedFile.PRESSURE_SWAY_L).first()
        tdRight = participant.trainingData.filter(pressure_type=UploadedFile.PRESSURE_SWAY_R).first()
        
        (mappedPointsLeft, csvRowLeft) = getMappedTrainingData(tdLeft.id)
        (mappedPointsRight, csvRowRight) = getMappedTrainingData(tdRight.id)
        
        
        for pointLeft  in mappedPointsLeft:
            (x,y) = pointLeft['points']
            pointType = pointLeft['pointType']
            
            
            paramsLeft.points.append({
                "x":x,
                "y":y,
                "pointType":pointType
            })
            
            
        
        for pointRight in mappedPointsRight:
            (x,y) = pointRight['points']
            pointType = pointRight['pointType']
            
            paramsRight.points.append({
                "x":x,
                "y":y,
                "pointType":pointType
            })
            
        
        # generate the response
        data = {
            'leftParameters':paramsLeft,
            'rightParameters':paramsRight,
            'participant':participant
        }
        
        s = ParticipantInsoleSerializer(data)
        
        return Response(s.data)
        
        return Response({'status': 'password set'})


from django.http import HttpResponse
from django.views.generic import View

from django.http import StreamingHttpResponse




def longTaskTest(request):
    return render(request, 'longTaskTest.html')


def LongTaskView(request):
    
    def generate():
        for i in range(1, 11):
            # Do some work here
            time.sleep(1)  # Simulate work taking 1 second

            # Yield progress update to the client
            yield f"data: Task progress: {i*10}%\n\n"
    
        # Signal task completion
        yield 'data: Task complete\n\n'
        
    response = StreamingHttpResponse(generate(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    #response['Connection'] = 'keep-alive'
    
    return response
    
    