from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
import os
from participants.helpers.painPoints import renderPainPointsOfParticipant
from participants.helpers.shoes import GERMAN_SHOE_SIZES
import math

# Create your models here.

class DataProtection(models.Model):
    created = models.DateTimeField(_("Erstellt"), auto_now=False, auto_now_add=True)
    svg = models.TextField(blank=False, null=False)
    email = models.EmailField(blank=True, null=True)
    email_sent = models.BooleanField(_("E-Mail verschickt"), default=False, blank=True)
    name = models.CharField(blank=True, null=True, max_length=250)
    pdf = models.FileField(upload_to="dataprotection", blank=True, null=True)

    checksum = models.CharField(max_length=64, blank=True, )

    public_id = models.IntegerField(default=-1, blank=False, help_text="")
    
    def __str__(self):
        return "[(%s) -> %s] %s" % (self.id, self.public_id, self.created)


from PIL import Image, ImageDraw, ImageFont
import os
from django.db.models import Q

class Participant(models.Model):
    lock_sync = models.BooleanField(default=False, help_text=_("Wenn True, dann wird kein Sync vom Client erlaubt"))
    
    
    GENDER_CHOICES = (
        ("m",_('männlich')),
        ("w",_('weiblich')),
        ("d",_('divers')),
        ("-",'-'),
        )
    
    created = models.DateTimeField(_("Erstellt"), auto_now=False, auto_now_add=True)
    active = models.BooleanField(_("aktiv"), default=False, blank=True)
    
    filled_out_questionnaire = models.BooleanField(_("Fragebogen ausgefüllt"), default=False, blank=True)    
    signed_dataprotection = models.BooleanField(_("Teilnehmer*in hat Datenschutzerklärung unterschrieben"), default=False, blank=True)
    foam_footprint = models.BooleanField(_("Teilnehmer*in hat Fußabdruck abgegeben"), default=False, blank=True)
    pressure_plate_done = models.BooleanField(_("Teilnehmer*in ist über Druckmessplatte gelaufen"), default=False, blank=True)
    pressure_plate_upload_done = models.BooleanField(_("Dateien hochgeladen"), default=False, blank=True)
    participant_compensated = models.BooleanField(_("Teilnehmer*in hat Kompensation erhalten"), default=False, blank=True)
    desinfected_everything = models.BooleanField(_("Alles desinfiziert"), default=False, blank=True)
    
    public_id = models.IntegerField(default=-1, blank=False, help_text="")
    
    def __str__(self):
        return "[(DB: %s) -> GAI: %s] %s" % (self.id, self.public_id, self.created)
    
    @property
    def files_uploaded(self):
        return False

    @property
    def uploaded_foam_imprints(self):
        return self.uploads.filter(upload_type=UploadedFile.FOAM_PRINT)
    
    @property
    def uploaded_foam_imprint(self):
        return self.uploaded_foam_imprints.first()
    
       
    @property
    def foamPrintAnalysed(self):
        fp = self.uploaded_foam_imprint
        if fp == None:
            return False
        
        try:
            analysis = fp.foamprintanalysis.leftFoot.url
        except:
            return False
        
        return True
        
    
    @property
    def completed(self):
        return self.filled_out_questionnaire and self.signed_dataprotection and self.foam_footprint and self.pressure_plate_done and self.pressure_plate_upload_done and  self.participant_compensated and self.desinfected_everything
    
    @property
    def has_uploaded_foam(self):
        return self.uploads.filter(upload_type=UploadedFile.FOAM_PRINT).count()>0
    
    @property
    def files_okay(self):
        # checks if all files have a plausible file name, i.e. they contain the public id of this participant
        all_okay = True
        
        try:
            for f in self.uploads.filter(upload_type__in=[UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_SWAY_R, UploadedFile.PRESSURE_WALK_L, UploadedFile.PRESSURE_WALK_R]):
                # get filename
                if f.file != None:
                    #print(f.file.path)
                    try:
                        basename_0 = os.path.basename(f.file.path).split("_")[0]
                        basename_1 = os.path.basename(f.file.path).split("_")[1]
                    except:
                        continue
                    
                    #print("%s %s" % (basename_0, basename_1))
                    if not basename_0 == str(self.public_id) and not basename_1 == str(self.public_id):
                        all_okay = False
        except:
            pass
        
        return all_okay

    age = models.IntegerField(_("Alter"), null=True, blank=False)
    height = models.IntegerField(_("Größe in cm"),  null=True, blank=False)
    weight = models.IntegerField(_("Gewicht in kg"), null=True, blank=False)
    gender = models.CharField(_("Geschlecht"), max_length=3, default="-", null=False, blank=False, choices=GENDER_CHOICES)
    
    heel_spur_left = models.BooleanField(_("Fersensporn links"), default=False, blank=True, help_text=_("Ein Fersensporn ist eine wenige Millimeter kleine dornartige Verknöcherung an der Ferse."))
    heel_spur_right = models.BooleanField(_("Fersensporn rechts"), default=False, blank=True)
    
    leg_shortening_left = models.IntegerField(_("Verkürzungsausgleich links in cm"), default="0",blank=False, help_text=_("Ein Verkürzungsausgleich dient u.a. zum Ausgleich einer Beinverkürzung sowie Skoliose"))
    leg_shortening_right = models.IntegerField(_("Verkürzungsausgleich rechts in cm"), default="0",blank=False)
    
    
    
    shoe_size = models.FloatField(_("Schuhgröße"), null=True ,blank=False, choices=GERMAN_SHOE_SIZES)
    
    pain_points = models.JSONField(_("Schmerzpunkte"), default=dict, blank=True)
    pain_points_render = models.FileField(upload_to="pain_points", blank=True, null=True)
    
    
    comments_participant = models.TextField(_("Kommentare Teilnehmer"), default="", blank=True)
    comments_experimenter = models.TextField(_("Kommentare Experimenter"), default="", blank=True)
    
    
    def renderPainPoints(self):
        renderPainPointsOfParticipant(self)
    
    @property
    def pressureCount(self):
        return {
            "walk_left":self.uploads.filter(upload_type=UploadedFile.PRESSURE_WALK_L).count(),
            "walk_right":self.uploads.filter(upload_type=UploadedFile.PRESSURE_WALK_R).count(),
            "sway_left":self.uploads.filter(upload_type=UploadedFile.PRESSURE_SWAY_L).count(),
            "sway_right":self.uploads.filter(upload_type=UploadedFile.PRESSURE_SWAY_R).count(),
            "foam":self.uploads.filter(upload_type=UploadedFile.FOAM_PRINT).count()
        }
        
    @property
    def videoProgress(self):
        csvs = self.csvs
        
        woAnimation = csvs.filter(animation__isnull=True).count()
        
        return woAnimation == 0
    
    @property
    def videoProgressString(self):
        csvs = self.csvs
        
        woAnimation = csvs.filter(animation__isnull=True).count()
        
        return "%s / %s" % (csvs.filter(animation__isnull=False).count(), csvs.count())
        
    
    @property
    def insoleProgress(self):
        # get all alignments
        progress = 0

        if self.insoleparameterleft.laenge_der_einlage != 0:
            progress += 50
        
        if self.insoleparameterright.laenge_der_einlage != 0:
            progress += 50
        
        
        return progress

    @property
    def alignmentProgress(self):
        # get all alignments
        allData = self.trainingData.all().count()
        editedData = self.trainingData.filter(~Q(pressure_rot=0)).count()
        
        if allData == 0:
            return 0
        
        progress =  math.floor((editedData / allData)*100)
        
        return progress

    @property
    def csvs(self):
        return self.uploads.filter(upload_type__in = [UploadedFile.PRESSURE_WALK_L, UploadedFile.PRESSURE_WALK_R, UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_SWAY_R] )
    
    @property
    def leftInsole(self):
        return self.insoleparameterleft

    
    @property
    def rightInsole(self):
        return self.insoleparameterright

    @property
    def left_csvs(self):
        return self.uploads.filter(upload_type__in = [UploadedFile.PRESSURE_WALK_L,  UploadedFile.PRESSURE_SWAY_L] )

    @property
    def left_walk(self):
        return self.uploads.filter(upload_type__in = [UploadedFile.PRESSURE_WALK_L] ).first()

    @property
    def left_sway(self):
        return self.uploads.filter(upload_type__in = [UploadedFile.PRESSURE_SWAY_L] ).first()

    @property
    def right_walk(self):
        return self.uploads.filter(upload_type__in = [UploadedFile.PRESSURE_WALK_R] ).first()

    @property
    def right_sway(self):
        return self.uploads.filter(upload_type__in = [UploadedFile.PRESSURE_SWAY_R] ).first()


    @property
    def right_csvs(self):
        return self.uploads.filter(upload_type__in = [UploadedFile.PRESSURE_WALK_R,  UploadedFile.PRESSURE_SWAY_R] )

    @property
    def analyzedFoamPrint(self):
        foamPrintUpload = None

        try:
            foamPrintUpload = self.uploads.filter(upload_type=UploadedFile.FOAM_PRINT).first()
        except Exception as e:
            print(e)
            return None

        
        foamPrintAnalysis = foamPrintUpload.foamprintanalysis
        
        return foamPrintAnalysis

        
    
    pass


##### Signals

@receiver(pre_save, sender=Participant)
def participant_pre_save(sender, instance, **kwargs):
    instance.renderPainPoints()
    

@receiver(post_save, sender=Participant)
def participant_created(sender, instance, created, **kwargs):
    #instance.renderPainPoints()
    if not kwargs.get('raw', False):

        if instance.public_id == -1:
            # calculate the next public_id
            instance.public_id = instance.id
            instance.save()
        

class UploadedFile(models.Model):    
    FOAM_PRINT = "foam"    
    
    PRESSURE_STAND = "stand"   #legacy
    PRESSURE_SWAY = "sway"    #legacy
    PRESSURE_WALK = "walk"    #legacy
    
    
    PRESSURE_SWAY_L = "sway_l"
    PRESSURE_SWAY_R = "sway_r"
    
    PRESSURE_WALK_L = "walk_l"
    PRESSURE_WALK_R = "walk_r"
    
    
    
    OTHER = "other"
    
    CHOICES = (
        (FOAM_PRINT, FOAM_PRINT),
        (PRESSURE_WALK, PRESSURE_WALK),     #legacy
        (PRESSURE_STAND, PRESSURE_STAND),   #legacy
        (PRESSURE_SWAY, PRESSURE_SWAY),     #legacy
        
        (PRESSURE_WALK_L, PRESSURE_WALK_L),
        (PRESSURE_WALK_R, PRESSURE_WALK_R),
        
        (PRESSURE_SWAY_L, PRESSURE_SWAY_L),
        (PRESSURE_SWAY_R, PRESSURE_SWAY_R),
        
        (OTHER, OTHER),        
    )
    
    created = models.DateTimeField(auto_now_add=True)
    participant = models.ForeignKey(Participant, null=True, on_delete=models.CASCADE, related_name="uploads")
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    upload_type = models.CharField(max_length=20, blank=False, default=OTHER, choices=CHOICES)    
    checksum = models.CharField(max_length=64, blank=True, )

    def __str__(self):
        return "[(%s)] %s - %s - %s" % (self.id, self.created, self.upload_type, self.file.name)
    
    def writeChecksum(self):
        checksum = None
        if os.path.isfile(self.file.path):            
            with open(self.file.path, 'rb') as file:
                file.seek(0)
                checksum = hashlib.sha256(file.read()).hexdigest()
                file.seek(0)            
                self.checksum=checksum
                self.save()
        return checksum
    
import hashlib



@receiver(post_delete, sender=UploadedFile)
def delete_file(sender, instance, **kwargs):
    # Delete the file from the storage
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
  
    
    
@receiver(post_delete, sender=Participant)
def delete_file(sender, instance, **kwargs):
    # Delete the file from the storage
    if instance.pain_points_render:
        if os.path.isfile(instance.pain_points_render.path):
            os.remove(instance.pain_points_render.path)          
    
    
@receiver(post_delete, sender=DataProtection)
def delete_file_dataprotection(sender, instance, **kwargs):
    # Delete the file from the storage
    if instance.pdf:
        if os.path.isfile(instance.pdf.path):
            os.remove(instance.pdf.path)
#post_delete.connect(create_subdirectory, sender=Participant)