from django.core.management.base import BaseCommand
from  synchronizer.helpers import sync
from participants.models import *

class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('--ids', nargs="+", type=int, help='The greenAI IDs of the participant')
        parser.add_argument('--startAt', nargs=1,  help="Start at this greenAI Ids, ascending")
        

    def handle(self, *args, **options):
        print(options)
        
        ids = options['ids']
        start_at = options['startAt']
        
        if ids:
            print("Ids...")
            for participant_id in options['ids']:
            #print(participant_id)
                print("Finding participant with greenAI Id %s" % participant_id)
                participant = Participant.objects.get(public_id=participant_id)
                sync.syncParticipant(participant.id)
                
            return
        
        if start_at:
            print("Start at..")
            for p in Participant.objects.filter(pk__gte=int(start_at[0])).order_by('id',):
                print(p.id)
                sync.syncParticipant(p.id)
            
            return
        
        return
        
        
        for participant_id in options['ids']:
            #print(participant_id)
            print("Finding participant with greenAI Id %s" % participant_id)
            participant = Participant.objects.get(public_id=participant_id)
            sync.syncParticipant(participant.id)
        return
        
        participant_id = options['id']

        if participant_id != None:
            # try and find the greenAi id
            print("Finding participant with greenAI Id %s" % participant_id)
            participant = Participant.objects.get(public_id=participant_id)
            sync.syncParticipant(participant.id)
        
        else:
            confirmation = input('This will upload all data participant data. Proceed? (y/n): ')

            if confirmation.lower() != 'y':
                self.stdout.write(self.style.ERROR('Command execution aborted'))
                return
            
            for p in Participant.objects.all():
                print("syncing %s" % p)
                sync.syncParticipant(p.id)
        
        
