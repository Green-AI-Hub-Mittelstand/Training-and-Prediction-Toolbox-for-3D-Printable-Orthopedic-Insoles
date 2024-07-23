from django.db import models
from dataInspection.helpers.pois import FOAM_POINT_CHOICES, FoamPointDefinitions, get_label_for_value
from participants.models import *
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete, pre_save


# Create your models here.

class AnimatedPressure(models.Model):
    uploadedFile = models.OneToOneField(UploadedFile, null=False, blank=False, on_delete=models.CASCADE, related_name="animation")    
    animation = models.FileField(upload_to='feet-animation', blank=True, null=True)
    animationPoster = models.FileField(upload_to='feet-animation', blank=True, null=True)
    
    def __str__(self):
        return "[%s] AnimatedPressure %s" % (self.id, self.uploadedFile.participant)


@receiver(post_delete, sender=AnimatedPressure)
def delete_fp_file(sender, instance, **kwargs):
    # Delete the file from the storage
    
    for field in ['animation','animationPoster']:
        file_field = getattr(instance, field)
        if file_field:
            if os.path.isfile(file_field.path):
                os.remove(file_field.path)

from django.db.models import Count, Subquery

class FoamPrintAnalysis(models.Model):
    uploadedFile = models.OneToOneField(UploadedFile, null=False, blank=False, on_delete=models.CASCADE)

    leftFoot = models.FileField(upload_to='feet/', blank=True, null=True)
    rightFoot = models.FileField(upload_to='feet/', blank=True, null=True)
    
    scaledImage = models.FileField(upload_to='feet/', blank=True, null=True, help_text="This is the correctly scaled image")
    
    scalingFactor = models.FloatField(blank=True, null=True,help_text="This either needs to be set by the program or the user - fallback")

    @property
    def pointsLeft(self):
        return self.points.filter(foot=FoamPrintPoint.LEFT)
    

    @property
    def pointsRight(self):
        return self.points.filter(foot=FoamPrintPoint.RIGHT)
    
    
    def _checkPoints(self, points):
        
        duplicate_ids_subquery = points.exclude(pointType=-1).values('pointType').annotate(pointType_count=Count('pointType')).filter(pointType_count__gt=1).values('pointType')

        # Query to get instances of YourModel with uploadType that occur more than once
        result_queryset = points.exclude(pointType=-1).filter(pointType__in=Subquery(duplicate_ids_subquery))
        
        
        doublePoints = points.exclude(pointType=-1).values('pointType').annotate(pointType_count=Count('pointType')).filter(pointType_count__gt=1)
        
        
        
        found_point_types = points.exclude(pointType=-1).values_list('pointType', flat=True)
        
        missingPointTypes = []
        
        ### find points that are missing
        
        for (key, label) in FOAM_POINT_CHOICES:
            #print(key)
            if key != -1:
                if not key in found_point_types:
                    missingPointTypes.append(key)
        
        res = {
            "foundAllPoints":len(points) == len(FOAM_POINT_CHOICES) -1,
            "missingPointsNum":len(FOAM_POINT_CHOICES) -1 - len(points),
            "identifiedAllPoints":points.filter(pointType=-1).count() == 0,
            "unidentifiedPointsNum":points.filter(pointType=-1).count(),
            "duplicatePointsNum":doublePoints.count(),
            "duplicatePoints":result_queryset,
            "missingPointTypes":missingPointTypes
        }
        
        res["ok"] = res["foundAllPoints"] and res["identifiedAllPoints"] and res["duplicatePointsNum"] ==0
        
        return res

    
    
    @property
    def pointsRightComplete(self):        
        return self._checkPoints(self.pointsRight)
    
    @property
    def pointsLeftComplete(self):
        # points are complete if the number if correct and there is no point that has is not recognized
        return self._checkPoints(self.pointsLeft)
    
    @property
    def participant(self):
        return str(self.uploadedFile.participant)
    

    def __str__(self):
        return "[%s] FoamPrint %s" % (self.id, self.uploadedFile.participant)


@receiver(post_delete, sender=FoamPrintAnalysis)
def delete_fp_file(sender, instance, **kwargs):
    # Delete the file from the storage
    
    for field in ['leftFoot','rightFoot','scaledImage']:
        file_field = getattr(instance, field)
        if file_field:
            if os.path.isfile(file_field.path):
                os.remove(file_field.path)


class FoamPrintPoint(models.Model):
    LEFT = "left"
    RIGHT = "right"

    FOOT_CHOICES = (
        (LEFT, LEFT),
        (RIGHT, RIGHT),
    )

    foamPrintAnalysis = models.ForeignKey(FoamPrintAnalysis, null=False, blank=False, on_delete=models.CASCADE, related_name="points")
    x = models.IntegerField(blank=False, null=False)
    y = models.IntegerField(blank=False, null=False)
    pointType = models.IntegerField(null=False, blank=False, choices=FOAM_POINT_CHOICES, default=FoamPointDefinitions.UNRECOGNIZED)

    foot = models.CharField(max_length=100, blank=False, default="left", choices=FOOT_CHOICES)
    
    @property
    def pointTypeVerbose(self):
        return get_label_for_value(self.pointType)
    
    def  __str__(self):
        return "[%s] FoamPrintPoint %s -> %s " % (self.id, self.foamPrintAnalysis, get_label_for_value(self.pointType) )
    

class PressurePlateAnalysis(models.Model):
    uploadedFile = models.OneToOneField(UploadedFile, null=False, blank=False, on_delete=models.CASCADE)
    
    def __str__(self):
        return "[%s] PressurePlateAnalysis %s" % (self.id, self.uploadedFile.participant)



class InsoleParameters(models.Model):
    SCORE_CHOICES_10 = [(0,"nein")] + list(zip( range(1,11), range(1,11) ))
    SCORE_CHOICES_10_mm = [(0,"nein")] + list(zip( range(1,11), range(1,11) ))
    SCORE_CHOICES_15_mm = [(0,"nein")] + list(zip( range(1,16), range(1,16) ))
    
    PELOTTEN_FORM_CHOICES = [
        (0,"Schmal"),
        (1,"Breit"),
        (2,"Stufe"),
    ]
    
    participant = models.OneToOneField(Participant, null=False, blank=False, on_delete=models.CASCADE )
    
    
    laenge_der_einlage = models.IntegerField(default=0, verbose_name=_("Länge der Einlage"), help_text="Fußlänge + 10mm")
    breit_der_einlage_im_vorfussbereich = models.IntegerField(default=0, verbose_name=_("Breit der Einlage im Vorfußbereich"), help_text="Vorfußbreite")
    breite_der_einlage_im_rueckfussbereich = models.IntegerField(default=0, verbose_name=_("Breite der Einlage im Rückfußbereich"), help_text="Rückfußbreite")
    
    mfk_1_entlasten = models.IntegerField(default=0,  choices=SCORE_CHOICES_10, verbose_name=_("MFK 1 entlasten"))
    mfk_2_entlasten = models.IntegerField(default=0,  choices=SCORE_CHOICES_10, verbose_name=_("MFK 2 entlasten"))
    mfk_3_entlasten = models.IntegerField(default=0,  choices=SCORE_CHOICES_10, verbose_name=_("MFK 3 entlasten"))
    mfk_4_entlasten = models.IntegerField(default=0,  choices=SCORE_CHOICES_10, verbose_name=_("MFK 4 entlasten"))
    mfk_5_entlasten = models.IntegerField(default=0,  choices=SCORE_CHOICES_10, verbose_name=_("MFK 5 entlasten"))  
    
    zehe_1_entlasten = models.IntegerField(default=0, choices=SCORE_CHOICES_10,  verbose_name=_("Zehe 1 entlasten"))
    zehe_2_entlasten = models.IntegerField(default=0, choices=SCORE_CHOICES_10,  verbose_name=_("Zehe 2 entlasten"))
    zehe_3_entlasten = models.IntegerField(default=0, choices=SCORE_CHOICES_10,  verbose_name=_("Zehe 3 entlasten"))
    zehe_4_entlasten = models.IntegerField(default=0, choices=SCORE_CHOICES_10,  verbose_name=_("Zehe 4 entlasten"))
    zehe_5_entlasten = models.IntegerField(default=0, choices=SCORE_CHOICES_10,  verbose_name=_("Zehe 5 entlasten"))
    
    pelotten_hoehe = models.IntegerField(default=0, choices=SCORE_CHOICES_10,  verbose_name=_("Pelottenhöhe"))    
    
    pelotten_form = models.IntegerField(default=0, choices=PELOTTEN_FORM_CHOICES,  verbose_name=_("Pelottenform"))   
    
    laengsgewoelbe_hoehe = models.IntegerField(default=0, choices=SCORE_CHOICES_10,  verbose_name=_("Längsgewölbe-Höhe"))    
    basis_5_entlasten = models.IntegerField(default=0, choices=SCORE_CHOICES_10,  verbose_name=_("Basis 5 entlasen"))
    
    fersensporn = models.BooleanField(default=False, verbose_name=_("Fersensporn"))
    
    aussenrand_anheben = models.IntegerField(default=0,  choices=SCORE_CHOICES_10_mm, verbose_name=_("Außenrand anheben (mm)"))
    innenrand_anheben = models.IntegerField(default=0,  choices=SCORE_CHOICES_10_mm, verbose_name=_("Innerand anheben (mm)"))
    verkuerzungsausgleich = models.IntegerField(default=0,  choices=SCORE_CHOICES_15_mm, verbose_name=_("Verkürzungsausgleich (mm)"))
    
    
    comments = models.TextField(blank=True, null=True, help_text="Diverse Kommentare")
    class Meta:
        abstract=True
        
class InsoleParameterLeft(InsoleParameters):
    pass

class InsoleParameterRight(InsoleParameters):
    pass

class TrainingData(models.Model):
    PRESSURE_TYPE_CHOICES = [
        (UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_SWAY_L),
        (UploadedFile.PRESSURE_SWAY_R, UploadedFile.PRESSURE_SWAY_R),
        (UploadedFile.PRESSURE_WALK_L, UploadedFile.PRESSURE_WALK_L),
        (UploadedFile.PRESSURE_WALK_R, UploadedFile.PRESSURE_WALK_R),
    ]
    
    FIT_QUALIY_CHOICES = [
        (0, _("schlecht")),
        (1, _("mittel")),
        (2, _("gut")),
    ]
    
    pressure_type = models.CharField(max_length=100, blank=True, null=True, default=UploadedFile.PRESSURE_SWAY_L, choices=PRESSURE_TYPE_CHOICES)
    
    participant = models.ForeignKey(Participant, null=False, blank=False, on_delete=models.CASCADE, related_name="trainingData")
    
    foamPrint = models.ForeignKey(FoamPrintAnalysis, blank=False, null=False, on_delete=models.CASCADE)
    pressurePlate = models.OneToOneField(PressurePlateAnalysis, blank=False, null=False, on_delete=models.CASCADE)

    
    validated = models.BooleanField(default=False)
    
    fit_quality = models.IntegerField(default=2, choices=FIT_QUALIY_CHOICES)

    pressure_x = models.IntegerField(default=0, blank=True, help_text="Horizontal translation of the pressure image on the foam print image")
    pressure_y = models.IntegerField(default=0, blank=True, help_text="Vertical translation of the pressure image on the foam print image")
    pressure_rot = models.FloatField(default=0.0, blank=True, help_text="Rotation of the pressure image on the foam print image")
    
    def __str__(self):
        return "Aligned Pressure Image %s (GAID: %s)" % (self.id, self.participant.public_id)

    @property
    def foot(self):
        if self.pressure_type in [UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_WALK_L]:
            # this is left
            return "left"
        
        if self.pressure_type in [UploadedFile.PRESSURE_SWAY_R, UploadedFile.PRESSURE_WALK_R]:
            return "right"
        
        raise Exception("This training data %s is not of a foot" % str(self) )
        
        



    @property
    def footPrintPoints(self):
        if self.pressure_type in [UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_WALK_L]:
            # this is left
            return self.foamPrint.pointsLeft
        else:
            # this is right
            return self.foamPrint.pointsRight


    @property
    def footPrintUrl(self):
        if self.pressure_type in [UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_WALK_L]:
            # this is left
            return self.foamPrint.leftFoot.url
        else:
            # this is right
            return self.foamPrint.rightFoot.url





    @property
    def footPrintFile(self):
        if self.pressure_type in [UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_WALK_L]:
            # this is left
            return self.foamPrint.leftFoot.path
        else:
            # this is right
            return self.foamPrint.rightFoot.path
        
    class Meta:
        verbose_name = "Aligned Pressure Recording (TrainingData)"
        verbose_name_plural = "Aligned Pressure Recordings (TrainingData)"
        

   

from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver


@receiver(post_delete, sender=TrainingData)
def delete_related_object(sender, instance, **kwargs):
    # Delete the associated FoamPrint object when a RelatedModel object is deleted - no, do not do that...
    
    return False
    
    #try:
    #    instance.foamPrint.delete()
    #except Exception as e:
    #    #raise e
    #    print("could not delete foamPrint for TrainingData %s" % instance.id)
    #    print(e)
    

    # try:
    #     instance.pressurePlate.delete()
    # except:
    #     print("could not delete pressurePlate for TrainingData %s" % instance.id)
    #     pass

        
    # try:
    #     instance.insoleParameters.delete()
    # except:
    #     print("could not delete insoleParameters for TrainingData %s" % instance.id)
        
    