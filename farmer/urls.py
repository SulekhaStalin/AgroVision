from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_farmer, name='farmer_register'),
    path('login/', views.farmer_login, name='farmer_login'),
    path('logout/', views.farmer_logout, name='farmer_logout'),
    path('dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('add-crop/', views.add_crop, name='add_crop'),
    path('edit-crop/<int:crop_id>/', views.edit_crop, name='edit_crop'),
    path('delete-crop/<int:crop_id>/', views.delete_crop, name='delete_crop'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('add-sale/', views.add_sale, name='add_sale'),
]