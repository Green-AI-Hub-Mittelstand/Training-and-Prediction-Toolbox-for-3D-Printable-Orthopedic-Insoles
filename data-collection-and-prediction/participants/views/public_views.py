
from .views import ParticipantForm
from django.shortcuts import render


def public_data_protection(request):
    
    return render(request, "participant_data_protection_public.html",  )


def public_questionnaire(request):
    form = ParticipantForm()
    return render(request, "participant.html", {"form":ParticipantForm} )