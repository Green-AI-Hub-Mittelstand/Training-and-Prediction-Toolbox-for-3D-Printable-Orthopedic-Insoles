from django.core.management.base import BaseCommand
from  synchronizer.helpers import sync
from participants.models import *

class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('ids',  type=int, nargs="+", help='The IDs, separated by whitespace')

    def handle(self, *args, **options):
        participant_ids = options['ids']

        for p in participant_ids:
            sync.downloadParticipant(p)
        
        