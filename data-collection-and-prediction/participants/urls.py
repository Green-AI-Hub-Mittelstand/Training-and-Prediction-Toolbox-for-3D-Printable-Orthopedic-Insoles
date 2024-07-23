from django.urls import path

from .views import views
from .views import rest_views, preview_views, public_views


urlpatterns = [
    path("", views.index, name="landing"),
    path("upload", views.upload_file, name="upload"), # for files from the experimenter views
    
    path("participant_overview", views.participant_overview, name="participant_overview"),    
    path("participant", views.participant, name="participant"),
    path("sign-data-protection", views.dataProtection, name="sign-data-protection"),
    path("experimenter", views.experimenter, name="experimenter"),
    path("experimenter/<int:participant_id>/", views.experimenter, name="experimenter_p_choice"),
    path("experimenter/new", views.new_participant, name="new_participant"),

    path("recording-instructions", views.recording_instructions, name="recording-instructions"),

    path("imprintRecorder", views.imprintRecorder, name="imprintRecorder"),


    path('link-file-to-uploaded-file/<int:file_id>/', rest_views.LinkFileToUploadedFileView, name='link-file-to-uploaded-file'), # this is for syncing
    path('link-file-to-data-protection/<int:data_protection_id>/', rest_views.LinkFileToDataProtectionView, name='link-file-to-data-protection'), # this is for syncing

    path("import-csv/<int:participant_id>/", views.import_csv_view, name="import_csv"),

    path('preview-upload/<int:id>/', preview_views.preview_upload, name='preview_upload'),
    #path('preview-upload/<int:id>/render_20_percent_view', preview_views.render20percentCSV, name='render20percentCSV'),
    path('preview-upload/<int:id>/render_20_percent_view_native', preview_views.render20percentNativeCSV, name='render20percentNativeCSV'),
    path('preview-upload/<int:id>/render_20_percent_view_native/<int:row>', preview_views.render20percentNativeCSV, name='render20percentNativeCSVRow'),

    path('preview-alignment/<int:id>',preview_views.renderAlignment,  name="renderAlignment"),
    path('preview-mapping/<int:id>',preview_views.renderMappingOrig,  name="renderMappingOrig"),
    path('preview-mapping/<int:id>/cropped',preview_views.renderMappingCropped,  name="renderMappingCropped"),
    path('preview-mappingOnFoam/<int:id>',preview_views.renderMappingOnFoam,  name="renderMappingOnFoam"),
    
    
    path('preview-mapping/<int:training_data_id>/scaled/<int:scale>',preview_views.renderRawTrainingData,  name="renderRawTrainingData"),
    
    path('downloadTrainingData/<int:id>',preview_views.downloadTrainingData,  name="downloadTrainingData"),
    
    
    path('renderEnhancedFootprint/participant/<int:participant_id>/contrast/<int:contrast>/brightness/<int:brightness>/foot/<str:foot>', preview_views.renderEnhancedFootprint, name='renderEnhancedFootprint'),
    
    path('qrcode/',  views.QRCodeView.as_view(), name='qrcode'),
    
    #path('change_language/<str:language_code>/', views.change_language, name='change_language'),
    
    path("public/dataProtection", public_views.public_data_protection, name="public_data_protection"),
    path("public/questionnaire", public_views.public_questionnaire, name="public_questionnaire_protection"),
]
