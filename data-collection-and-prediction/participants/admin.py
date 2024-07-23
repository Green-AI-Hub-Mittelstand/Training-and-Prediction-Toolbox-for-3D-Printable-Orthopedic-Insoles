
from django.contrib import admin

from dataInspection.helpers.housekeeeping import createTrainingDataForParticipant
from dataInspection.helpers.housekeepingAsync import createAnimationsForParticipantAsync, createTrainingDataForParticipantAsync

from .models import *

from dataInspection.helpers.animator import *

# Register your models here.





class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id','created','participant','upload_type','file','checksum')
    readonly_fields=('checksum',)
    
    list_filter = ('participant','upload_type')
    
    @admin.action(description="Animationen Erstellen")
    def prepare_animations(modeladmin, request, queryset):
         for f in queryset.filter(upload_type__in = [UploadedFile.PRESSURE_WALK_L, UploadedFile.PRESSURE_WALK_R, UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_SWAY_R] ):
            createAnimationForCSV(f.id)
             
            pass
        
    actions = ['prepare_animations']

admin.site.register(UploadedFile, UploadedFileAdmin)


class UploadInline(admin.TabularInline):
    model = UploadedFile
    
    
        
from django.contrib import messages    
  

from dataInspection.models import FoamPrintAnalysis

#class FoamPrintAnalysisInline(admin.TabularInline):
#    model = FoamPrintAnalysis

    
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id','public_id','foamPrintAnalysed', 'created','height','weight','gender','shoe_size','active','lock_sync','videoProgress',)
    inlines = [
        UploadInline,
        #FoamPrintAnalysisInline
    ]
    
    @admin.action(description="Trainingset für Participant erstellen")
    def prepare_training_set(modeladmin, request, queryset):
        for p in queryset.all():
            if not createTrainingDataForParticipant(p, request):
                messages.add_message(request, messages.WARNING, "Could not fully create datasets for participant %s" % p.id)
            
            pass
        
    @admin.action(description="[ASYNC] Trainingset für Participant erstellen")
    def prepare_training_set_async(modeladmin, request, queryset):
        for p in queryset.all():
            createTrainingDataForParticipantAsync.delay(p.id)
                
            
            pass
    
    
        
    @admin.action(description="[ASYNC] Create Animations")
    def prepare_animations_async(modeladmin, request, queryset):
        for p in queryset.all():
            createAnimationsForParticipantAsync(p)
                
            
            pass
    
    
    
    # @admin.action(description="[ASYNC] Animationen Erstellen")
    # def prepare_animations_async(modeladmin, request, queryset):
    #     for p in queryset.all():
    #         for f in p.uploads.filter(upload_type__in = [UploadedFile.PRESSURE_WALK_L, UploadedFile.PRESSURE_WALK_R, UploadedFile.PRESSURE_SWAY_L, UploadedFile.PRESSURE_SWAY_R] ):
    #             print(f)
                
            
            
    #         #createTrainingDataForParticipantAsync.delay(p.id)
                
            
    #         pass
    
        
    actions = [prepare_training_set_async, prepare_training_set, prepare_animations_async]
            
    

admin.site.register(Participant, ParticipantAdmin)



from import_export import resources
from import_export.admin import ImportExportModelAdmin

class DataProtectionResource(resources.ModelResource):

    class Meta:
        model = DataProtection  # or 'core.Book'

class DataProtectionAdmin(ImportExportModelAdmin):
    list_display = ('id','public_id','created','email','email_sent','name','pdf')
    resource_classes = [DataProtectionResource]
    

admin.site.register(DataProtection, DataProtectionAdmin)
