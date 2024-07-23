from django.urls import path

from .views import views



urlpatterns = [
    path("", views.landingUI, name="landingUI"),
    path("customer/<int:id>", views.customer, name="customer"), 
    path("customer/new", views.new_customer, name = "customer_new"),
    #path("customer/insoles/<int:insole_id>",views.customer_insole, name= "customer_insole"),
    
    path("customer/insoles/<int:insole_id>/point_predictor_status",views.point_predictor_status, name= "point_predictor_status"),
    
    path("customer/insoles/<int:insole_id>/point_editor",views.point_editor, name= "point_editor"),
    
    
    path("customer/insoles/<int:insole_id>/predict_points_view",views.predict_points_view, name= "predict_points_view"),
    
    path("customer/insoles/<int:insole_id>/predict_points_view_generator",views.predict_points_view_generator, name= "predict_points_view_generator"),
    
    
    
    
    
    path("customer/insoles/<int:insole_id>/param_editor",views.param_editor, name= "param_editor"),
    
    path("customer/insoles/<int:insole_id>/param_predictor_status",views.param_predictor_status, name= "param_predictor_status"),
    
    path("customer/insoles/<int:insole_id>/predict_params_view",views.predict_params_view, name= "predict_params_view"),
    
    
    
    
    path("customer/<int:id>/insoles/new",views.new_customer_insoles, name = "customer_insoles_new"),
    path("customer/<int:id>/insoles/copy",views.new_customer_insoles_copy_from_participant, name = "new_customer_insoles_copy_from_participant"),
    path("insoles/<int:insole_id>/<str:foot>",views.render20percentNativeCSVUI,
         name = "render20percentNativeCSVUI"),
    
    path("insoles/longTask",views.LongTaskView,
         name = "longTask"),
    
    path("insoles/longTaskTest", views.longTaskTest,name="longTaskTest")
    #path("customer/<int:customer_id>/insoles/<int:insole_id>/predict_points",views.predict_points,name = "predict_points"),
    #path("customer/<int:customer_id>/insoles/<int:insole_id>/predict_insole_parameters", views.predict_insole_parameters,name = "predict_insole_parameters")
]
