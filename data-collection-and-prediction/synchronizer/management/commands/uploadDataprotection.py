from django.core.management.base import BaseCommand
from  synchronizer.helpers import sync
from participants.models import *

class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='The ID of the dataprotection')

    def handle(self, *args, **options):
        dataprotectionId = options['id']

        if dataprotectionId != None:
            sync.syncDataprotection(dataprotectionId)

        else:
            confirmation = input('This will upload all data protection agreements. Proceed? (y/n): ')

            if confirmation.lower() != 'y':
                self.stdout.write(self.style.SUCCESS('Command execution aborted'))
                return
            
            for dp in DataProtection.objects.all():
                print("syncing %s" % dp)
                sync.syncDataprotection(dp.id)


        print(dataprotectionId)
        #sync.syncDataprotection(dataprotectionId)
        
