from django.contrib import admin
from .models import *

#from ui.helpers.predictPoints import createPredictionforCustomerLeft, #createPredictionforCustomerRight
#from ui.helpers.predictParameters import createPredictedInsoleParameters
# Register your models here.


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','height','weight','gender','shoe_size')

admin.site.register(Customer, CustomerAdmin)

class InsoleAdmin(admin.ModelAdmin):
    list_display = ('customer','created')

    """
    @admin.action(description="Punkt Predictions erstellen")
    def points_prediction(modeladmin,request,queryset):
        for p in queryset.all():
            createPredictionforCustomerLeft(p)
            createPredictionforCustomerRight(p)
            pass
    
    @admin.action(description="Einlagenparameter Predictions erstellen")
    def insole_prediction(modeladmin, request, queryset):
        for p in queryset.all():
            createPredictedInsoleParameters(p)
            pass
        
    
            
    actions = [points_prediction, insole_prediction]
    
    """
admin.site.register(Insole, InsoleAdmin)

class InsoleParametersProductionLeftAdmin(admin.ModelAdmin):
    list_display = ('id','insole',)    
admin.site.register(InsoleParametersProductionLeft, InsoleParametersProductionLeftAdmin)

class InsoleParametersProductionRightAdmin(admin.ModelAdmin):
    list_display = ('id','insole',)    
admin.site.register(InsoleParametersProductionRight, InsoleParametersProductionRightAdmin)



class PredictedPointLeftAdmin(admin.ModelAdmin):
    list_display = ('insole','x','y','pointType')
    list_filter = ('insole',)
    
admin.site.register(PredictedPointLeft,PredictedPointLeftAdmin)

class PredictedPointRightAdmin(admin.ModelAdmin):
    list_display = ('insole','x','y','pointType')
    list_filter = ('insole',)
    
admin.site.register(PredictedPointRight,PredictedPointRightAdmin)

