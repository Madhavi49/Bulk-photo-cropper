from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload', views.upload, name='upload'),
    path('resize', views.resize, name='resize'),
    path('process', views.process, name='process'),
    path('result', views.result, name='result'),
    path('download-all', views.download_all, name='download_all'),
]
