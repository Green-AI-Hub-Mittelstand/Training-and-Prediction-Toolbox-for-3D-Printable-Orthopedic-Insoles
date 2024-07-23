from django.db import models
from django.utils.translation import gettext_lazy as _
from participants.helpers.shoes import GERMAN_SHOE_SIZES
from dataInspection.helpers.pois import FOAM_POINT_CHOICES, FoamPointDefinitions, get_label_for_value

# Create your models here.


class Customer(models.Model):

    
    GENDER_CHOICES = (
        ("m",_('männlich')),
        ("w",_('weiblich')),
        ("d",_('divers')),
        ("-",'-'),
        )
    
    first_name = models.CharField(_("Vorname"), max_length=400, blank=False, null=False, default="")
    last_name = models.CharField(_("Nachname"), max_length=400, blank=False, null=False, default="")
    birthday = models.DateField(_("Geburtstag"), null=True, blank=False)
    height = models.IntegerField(_("Größe in cm"),  null=True, blank=False)
    weight = models.IntegerField(_("Gewicht in kg"), null=True, blank=False)
    gender = models.CharField(_("Geschlecht"), max_length=3, default="-", null=True, blank=True, choices=GENDER_CHOICES)
    
    heel_spur_left = models.BooleanField(_("Fersensporn links"), default=False, blank=True, help_text=_("Ein Fersensporn ist eine wenige Millimeter kleine dornartige Verknöcherung an der Ferse."))
    heel_spur_right = models.BooleanField(_("Fersensporn rechts"), default=False, blank=True)
    
    leg_shortening_left = models.IntegerField(_("Verkürzungsausgleich links in cm"), default="0",blank=False, help_text=_("Ein Verkürzungsausgleich dient u.a. zum Ausgleich einer Beinverkürzung sowie Skoliose"))
    leg_shortening_right = models.IntegerField(_("Verkürzungsausgleich rechts in cm"), default="0",blank=False)
    
    
    shoe_size = models.FloatField(_("Schuhgröße"), null=True ,blank=True, choices=GERMAN_SHOE_SIZES)
    
    pain_points = models.JSONField(_("Schmerzpunkte"), default=dict, blank=True)
    pain_points_render = models.FileField(upload_to="pain_points", blank=True, null=True)
    
    
    comments_customer = models.TextField(_("Kommentare Kund*in"), default="", blank=True)


class Insole(models.Model):
    customer = models.ForeignKey(Customer,null=False, blank = False,on_delete = models.CASCADE)
    created = models.DateTimeField(_("Erstellt"), auto_now = False, auto_now_add = True)
    
    pressureFileLeftWalk = models.FileField("Druckdaten Links (gehen)",upload_to='pressureFile/walk',blank = False, null = True)
    pressureFileRightWalk = models.FileField("Druckdaten Rechts (gehen)",upload_to='pressureFile/walk',blank = False, null = True)
    
    pressureFileLeftSway = models.FileField("Druckdaten Links (stehen)",upload_to='pressureFile/sway',blank = False, null = True)
    pressureFileRightSway = models.FileField("Druckdaten Rechts (stehen)",upload_to='pressureFile/sway',blank = False, null = True)
    

class InsoleParametersProduction(models.Model):

    SCORE_CHOICES_10 = [(0,"nein")] + list(zip( range(1,11), range(1,11) ))
    SCORE_CHOICES_10_mm = [(0,"nein")] + list(zip( range(1,11), range(1,11) ))
    SCORE_CHOICES_15_mm = [(0,"nein")] + list(zip( range(1,16), range(1,16) ))
    
    PELOTTEN_FORM_CHOICES = [
        (0,"Schmal"),
        (1,"Breit"),
        (2,"Stufe"),
    ]
    
    
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
    
    
    comments = models.TextField(verbose_name=_("Kommentare"),blank=True, null=True, help_text="Diverse Kommentare")
    class Meta:
        abstract=True
        
class InsoleParametersProductionLeft(InsoleParametersProduction):
    insole = models.OneToOneField(Insole, related_name="leftParameters", on_delete=models.CASCADE, null=True, blank=True)
    
    pass

class InsoleParametersProductionRight(InsoleParametersProduction):
    insole = models.OneToOneField(Insole, related_name="rightParameters", on_delete=models.CASCADE, null=True, blank=True)
    
    pass

"""
class PredictionsLeft(models.Model):
    insoles = models.ForeignKey(Insole,null = False, blank = False,on_delete=models.CASCADE,default = None)  
    insoleParameters = models.OneToOneField(InsoleParametersProductionLeft,null=True, blank=False, on_delete=models.CASCADE)

class PredictionsRight(models.Model):
    insoles = models.ForeignKey(Insole,null = False, blank = False,on_delete=models.CASCADE,default = None)  
    insoleParameters = models.OneToOneField(InsoleParametersProductionRight,null=True, blank=False, on_delete=models.CASCADE)
""" 

class PredictedPointLeft(models.Model):
    insole = models.ForeignKey(Insole, related_name="leftPoints", on_delete=models.CASCADE, null=True, blank=True)
    x = models.FloatField(blank=False, null=False)
    y = models.FloatField(blank=False, null=False)
    pointType = models.IntegerField(null=False, blank=False, choices=FOAM_POINT_CHOICES, default=FoamPointDefinitions.UNRECOGNIZED)

class PredictedPointRight(models.Model):
    insole = models.ForeignKey(Insole, related_name="rightPoints", on_delete=models.CASCADE, null=True, blank=True)
    x = models.FloatField(blank=False, null=False)
    y = models.FloatField(blank=False, null=False)
    pointType = models.IntegerField(null=False, blank=False, choices=FOAM_POINT_CHOICES, default=FoamPointDefinitions.UNRECOGNIZED)


