from django.contrib import admin
from .models import *
from .helpers.feetScanner import *
from django.core.files.base import ContentFile
from django.core.files import File

# Register your models here.


@admin.register(AnimatedPressure)
class AnimatedPressureAdmin(admin.ModelAdmin):
    list_display = ['id','uploadedFile','animation','animationPoster']    
    list_filter = []


class InsoleParametersAdmin(admin.ModelAdmin):
    list_display = ('id','participant','laenge_der_einlage')    

admin.site.register(InsoleParameterLeft, InsoleParametersAdmin)
admin.site.register(InsoleParameterRight, InsoleParametersAdmin)

class FoamPointsAdmin(admin.TabularInline):
    model = FoamPrintPoint


class FoamPrintAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id','uploadedFile','participant','scalingFactor')

    list_filter = ['uploadedFile__participant',]
    
    inlines = [
        FoamPointsAdmin,
    ]
    
    #@admin.action(description="Scan analysieren")
    def analyze_scan(modeladmin, request, queryset): # TODO, consolidate with housekeeping.py
        return 
        
        # for p in queryset.all():
        #     scanner_settings = FootScannerSettings()#155/175,5
            
        #     # Create FootScanner instances
        #     foot_scanner = FootScanner(scanner_settings)
        #     #print(p.uploadedFile.file.path)
        #     (result_right, result_left) = foot_scanner.scanImage(p.uploadedFile.file.path)

        #     flipped_l = foot_scanner.flipResultVertical(result_left)
        #     flipped_l = foot_scanner.flipResultHorizontal(flipped_l)
            
        #     store_result_to_model(flipped_l, p, True)    
            
                    
        #     flipped_r = foot_scanner.flipResultVertical(result_right)
        #     #flipped_r = foot_scanner.flipResultHorizontal(flipped_r)
        #     store_result_to_model(flipped_r, p, False)


        #     _, buffer = cv2.imencode('.jpg', foot_scanner.scaled_image) 
        #     image_bytes = buffer.tobytes()
        #     content_file = ContentFile(image_bytes)
        #     django_file = File(content_file)

        #     p.scaledImage.save('%s_scaled.jpg' % p.id, django_file)
        #     p.save()
            


        #     pass
        
    #actions = [analyze_scan]


admin.site.register(FoamPrintAnalysis, FoamPrintAnalysisAdmin)


class FoamPrintPointAdmin(admin.ModelAdmin):
    list_display = ('id','foamPrintAnalysis','x','y','pointTypeVerbose','point_type_int','foot',)
    
    @admin.display(ordering='-pointType', description='Point Type Int',)
    def point_type_int(self, obj):
        return int(obj.pointType)   
    

admin.site.register(FoamPrintPoint, FoamPrintPointAdmin)




class TrainingDataAdmin(admin.ModelAdmin):
    list_display = ('id','participant','foamPrint_id','pressurePlate_id', 'pressure_type','fit_quality')
    list_filter = ['participant']

admin.site.register(TrainingData, TrainingDataAdmin)

class PressurePlateAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id','uploadedFile',)

admin.site.register(PressurePlateAnalysis, PressurePlateAnalysisAdmin)
