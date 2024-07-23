from .housekeeeping import *
from participants.models import Participant
from .animator import *
from celery import shared_task


@shared_task
def createTrainingDataForParticipantAsync(participant_id):
    print("Preparing Participant %s" % participant_id)
    participant = Participant.objects.get(pk=participant_id)
    print("Public ID: %s" % participant.public_id)    
    createTrainingDataForParticipant(participant)
    print("### Training data for GAID %s done" % participant.public_id)
    
    """
    print("Dispatchting animation creation")
    for f in participant.csvs:
        createAnimationForCSVAsync.delay(f.id)
    print("### Dispatch animation for GAID %s done" % participant.public_id)
    """
    
    

@shared_task(name="createAnimationForCSVAsync", queue='videos')
def createAnimationForCSVAsync(uploadedFile_id):
    p = UploadedFile.objects.get(id=uploadedFile_id).participant
    print("Creating animation for file %s and GAID %s started" % (uploadedFile_id, p.public_id))
    
    
    createAnimationForCSV(uploadedFile_id)
    print("Creating animation for file %s and GAID %s done" %  (uploadedFile_id, p.public_id))
    
    

def createAnimationsForParticipantAsync(participant):
    
    for csv in participant.csvs:
        createAnimationForCSVAsync.delay(csv.id)
    
    
