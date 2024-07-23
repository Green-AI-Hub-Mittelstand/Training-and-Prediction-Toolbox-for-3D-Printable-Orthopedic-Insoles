from django.shortcuts import render

from participants.decorators import admin_required
from ..models import *
from django.forms import ModelForm, Form
from django import forms
from ..forms.widgets import CoordinateInput

from  django.shortcuts import redirect
from django.template import Template, Context
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import UploadedFile


from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

import ifaddr

# Create your views here.
@staff_member_required
def index(request):    
    
    adapters = ifaddr.get_adapters()
    
    ips = []

    for adapter in adapters:
        #print ("IPs of network adapter " + adapter.nice_name)
        for ip in adapter.ips:
            if isinstance(ip.ip, str):
                ips.append(ip.ip)
            #print ("   %s/%s" % (ip.ip, ip.network_prefix))
    
    
    return render(request, "landing.html", {'ips':ips})


class ParticipantForm(ModelForm):
    """Form definition for Participant."""

    class Meta:
        """Meta definition for Participantform."""

        model = Participant
        fields = ('age','height','weight','gender','shoe_size','leg_shortening_left','leg_shortening_right','heel_spur_left','heel_spur_right','pain_points','comments_participant')

        widgets = {
            'pain_points' : CoordinateInput(attrs={'id': 'pain_points','image_url':'feet-new.jpg','width':600,'height':659})
        }
        
        
@staff_member_required
def participant(request):
    
    # try and get the current active participant
    participant = Participant.objects.filter(active=True)
    
    print("Requested language: %s" % request.LANGUAGE_CODE)
    
    error = None
    if participant.count() > 1:
        error = "Es gibt mehr als einen aktiven Teilenhmer - hier ist wohl etwas schief gegangen."
    
    if participant.count() < 1:
        error = "Es gibt noch keinen aktiven Teilnehmer - bitte anlegen."
    
    if error is None:        
        # check if this person has already signed the data protection agreement
        if not participant.first().signed_dataprotection:
            return redirect("sign-data-protection")
        
        # load the model form
        p = participant.first()
        if request.method == "POST":
            form = ParticipantForm(request.POST, instance = p)
            if form.is_valid():                
                form.save()                
                p.refresh_from_db()
                p.filled_out_questionnaire = True
                p.save()
                #p.renderPainPoints()
                
                error = "Daten erfolgreich erfasst."
                return render(request, "participant_done.html", {"error":error,"error_title":"Erfolg!"})
            
                
        else:
            form = ParticipantForm(instance = p)
        
        return render(request, "participant.html", {"form":form, "participant":p})
    else:
        return render(request, "participant_error.html", {"error":error})

    
from fpdf import FPDF
from datetime import datetime
import uuid
import os
import shutil

from django.conf import settings
    
    
@staff_member_required
def dataProtection(request):
    
    # try and get the current active participant
    participant = Participant.objects.filter(active=True)
    
    error = None
    if participant.count() > 1:
        error = "Es gibt mehr als einen aktiven Teilenhmer - hier ist wohl etwas schief gegangen."
    
    if participant.count() < 1:
        error = "Es gibt noch keinen aktiven Teilnehmer - bitte anlegen."
    
    if participant.first().signed_dataprotection:
            return redirect("participant")
    
    if error is None:
                
        if request.method == "POST":
            signature = request.POST['signature']
            email = request.POST['email']
            name = request.POST['name']
            
            sig_filename = str(uuid.uuid4())+".svg"
            
            dpObject = DataProtection.objects.create(svg=signature, email=email, name=name)
            p = participant.first()
            p.signed_dataprotection = True
            p.save()
            
            # create pdf
            with open(sig_filename, "w") as file1:
                # Writing data to a file
                file1.write(signature)
                
            now = datetime.now() # current date and time
            date_time = now.strftime("%d.%m.%Y, %H:%M:%S")
            
            dp = render_to_string("data-protection.html") +"<br>"+date_time+"<img src='"+sig_filename+"' width='300'><br><br>"+dpObject.name 
            pdf = FPDF()
            pdf.add_page()
            pdf.write_html(dp)
            
                
            destination_folder = os.path.join(settings.MEDIA_ROOT, "dataprotection")
            
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            
            
                
            filename_pdf = os.path.join(destination_folder, "dataprotection-"+ str(dpObject.id * 12)+".pdf")
            dpObject.pdf.name = os.path.relpath(filename_pdf, settings.MEDIA_ROOT)
            dpObject.save()
            pdf.output(filename_pdf)
            #print(dp)



            with open(dpObject.pdf.path, 'rb') as file:
                file.seek(0)
                checksum = hashlib.sha256(file.read()).hexdigest()
                file.seek(0)            
                dpObject.checksum=checksum
                dpObject.public_id = dpObject.id
                dpObject.save()
                    
        
            
            
            os.remove(sig_filename)
            
            return redirect('participant')
        
        return render(request, "participant_data_protection.html",  )
    else:
        return render(request, "participant_error.html", {"error":error})


@admin_required
def experimenter(request, participant_id = None):
    # try and get the current active participant
    
    if participant_id == None:
    
        participant = Participant.objects.filter(active=True)
        
        error = None
        if participant.count() > 1:
            error = "Es gibt mehr als einen aktiven Teilenhmer - hier ist wohl etwas schief gegangen."
        
        if participant.count() < 1:
            return redirect("participant_overview")
            #error = "Es gibt noch keinen aktiven Teilnehmer - bitte anlegen."
        
        participant = participant.first()
    else:
        participant = get_object_or_404(Participant, pk=participant_id)
    
    return render(request, "experimenter_new.html", {"participant":participant})



@admin_required
def participant_overview(request):
    participants = Participant.objects.all().order_by("-public_id")
    
    return render(request, "participant_overview.html", {"participants":participants, "hasActive":Participant.objects.filter(active=True).count()>0})
    
    
@admin_required
def new_participant(request):
    if Participant.objects.filter(active=True).count() > 0:
        # there is already a participant, we reset it
        Participant.objects.filter(active=True).update(active=False)
    Participant.objects.create(active=True)
    return redirect("experimenter")


@csrf_exempt
@admin_required
def upload_file(request):
    if request.method == 'POST' and request.FILES:        
        participantId = request.POST["participant"]
        upload_type = request.POST["upload_type"]
        uploaded_file = request.FILES['file']
        new_file = UploadedFile(file=uploaded_file, participant_id=participantId, upload_type=upload_type)
        new_file.save()

        with new_file.file.open('rb') as file:
            checksum = hashlib.sha256(file.read()).hexdigest()
            new_file.checksum = checksum
            new_file.save()
        return JsonResponse({'message': 'File uploaded successfully!'})
    return JsonResponse({'message': 'Invalid request'}, status=400)

from ..helpers.importCSV import  importCSVforParticipant

@csrf_exempt
@admin_required
def import_csv_view(request, participant_id):
    
    participant = get_object_or_404(Participant, pk=participant_id)
    
    importCSVforParticipant(participant)
    
    return redirect(experimenter, participant_id=participant_id)
    

import os



@admin_required
def imprintRecorder(request):

    participants = Participant.objects.all().order_by('-created')

    context = {
        "participants":participants
    }


    participant_selection = []

    if request.method == "GET":
        start = request.GET.get("start_participant", None)
        end =  request.GET.get("end_participant", None)

    if request.method == "POST":
        start = request.POST.get("start_participant", None)
        end =  request.POST.get("end_participant", None)

        

    participant_selection = Participant.objects.order_by('-created')
    if start != None:
        participant_selection = participant_selection.filter(id__gte=start)
        context['start'] = int(start)

    if end != None:
        participant_selection = participant_selection.filter(id__lte=end)
        context['end'] = int(end)

    if start == None and end == None:
        participant_selection = []



    if request.method == "POST":
        # iterate over participants
        for p in Participant.objects.all():
            # try and get the file
            file = request.FILES.get('participant_'+str(p.id))
            if file:
                # create an uploaded file
                uploadedFile = UploadedFile.objects.create(participant=p, upload_type=UploadedFile.FOAM_PRINT)

                uploadedFile.file = file
                uploadedFile.save()
                with open(uploadedFile.file.path, 'rb') as file:
                    file.seek(0)
                    checksum = hashlib.sha256(file.read()).hexdigest()
                    file.seek(0)            
                    uploadedFile.checksum=checksum
                    uploadedFile.save()

        pass
        

    context['participant_selection'] = participant_selection
    
    return render(request, "imprintRecorder.html", context)

#@admin_required
def recording_instructions(request):
    return render(request, "recording-instructions.html")



# views.py
import qrcode
from django.http import HttpResponse
from django.views import View

class QRCodeView(View):
    def get(self, request, *args, **kwargs):
        # Get the text for the QR code
        text = request.GET.get('text', 'Default Text')

        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")

        # Create a response with the image content
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        return response



from django.shortcuts import redirect
from django.utils.translation import activate

def change_language(request, language_code):
    # Ensure that the language_code is valid before activating it
    supported_languages = ['en', 'de',]  # Add your supported languages here
    
    if language_code in supported_languages or True:
        activate(language_code)
        # Save the selected language in the user's session or database if needed
        request.session['django_language'] = language_code
        
    else:
        print("nooooo")
        # Handle invalid language codes, you can redirect to a default language or show an error page
        pass

    # Redirect back to the referring page or a specific URL
    redirect_url = request.META.get('HTTP_REFERER', '/')
    return redirect(redirect_url)