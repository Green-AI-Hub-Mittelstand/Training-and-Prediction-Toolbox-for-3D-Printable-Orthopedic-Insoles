from django.urls import path

from . import views


urlpatterns = [
    path("impressum", views.impressum, name="imprint"),
    path("datenschutz", views.datenschutz, name="dataprotection"),

    path("inspectParticipant/<int:participant_id>/", views.inspectParticipant, name="inspectParticipant"),
    path("inspectInsole/<int:participant_id>/", views.inspectInsole, name="inspectInsole"),
    path("inspectInsole/<int:participant_id>/videos", views.inspectVideos, name="inspectVideos")
    
]
