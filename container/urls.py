from django.urls import path

from container import views

urlpatterns = [
    path('create-new-container', views.create_new_container),
    path('save-code',views.save_code),
]
