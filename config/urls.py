from django.contrib import admin
from django.urls import path, include
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('farmer/', include('farmer.urls')),

    path('weather/', include('weather.urls')),

    path('plant-health/', include('plant_health.urls')),
]