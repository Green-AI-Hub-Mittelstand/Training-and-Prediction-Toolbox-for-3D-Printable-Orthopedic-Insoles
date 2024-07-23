"""
URL configuration for dataCollection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers

from participants.views import rest_views
from django_js_reverse.views import urls_js
from two_factor.urls import urlpatterns as tf_urls
from two_factor.admin import AdminSiteOTPRequired

from synchronizer.views import serve_media

from dataInspection import views as inspection_views
from ui.views import views as ui_views
#admin.site.__class__ = AdminSiteOTPRequired

router = routers.DefaultRouter()
router.register(r'participants', rest_views.ParticipantViewSet)
router.register(r'dataprotection', rest_views.DataProtectionViewSet)
router.register(r'uploadedfile', rest_views.UploadedFileViewSet)
router.register(r'inspection/foamPoint', inspection_views.FoamPrintPointViewSet)
router.register(r'inspection/trainingData', inspection_views.TrainingDataViewSet)
router.register(r'inspection/foamPrintAnalysis', inspection_views.FoamPrintAnalysisViewSet)

router.register(r'ui/predictionPointLeft',ui_views.PredictedPointLeftViewSet)
router.register(r'ui/predictionPointRight',ui_views.PredictedPointRightViewSet)


router.register(r'ui/customers',ui_views.CustomerViewSet)
router.register(r'ui/insoles',ui_views.InsoleViewSet)
router.register(r'ui/participants',ui_views.ParticipantViewSet, basename="ui_participants")


from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

#### doc
schema_view = get_schema_view(
   openapi.Info(
      title="GreenAI API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


###




urlpatterns = [
    path('admin/', include('massadmin.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    
    path('api/doc/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    path('jsreverse.js', urls_js, name='js_reverse'),
    
    path('media/<path:path>/', serve_media, name='serve_media'),
    #path('old', include("experiment_app.urls")),
    path('', include("participants.urls")),
    path('ui/', include("ui.urls")),
    
    path('inspect/', include("dataInspection.urls")),
    path('', include(tf_urls)),
    re_path(r'^rosetta/', include('rosetta.urls')),
    path("i18n/", include("django.conf.urls.i18n")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
