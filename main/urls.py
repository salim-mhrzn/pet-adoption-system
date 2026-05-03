from django.urls import path
from . import views

# main/urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('adopt/<int:pet_id>/', views.adopt_pet, name='adopt_pet'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:req_id>/', views.approve_request, name='approve_request'),
    path('reject/<int:req_id>/', views.reject_request, name='reject_request'),
    path('delete/<int:req_id>/', views.delete_adoption_request, name='delete_adoption_request'),
    path('notification/read/<int:notif_id>/', views.view_notification, name='view_notification'),
    path('reply/<int:msg_id>/', views.reply_message, name='reply_message'),
    path('dashboard/delete-message/<int:msg_id>/', views.delete_contact_message, name='delete_contact_message'),
    path('my-adoptions/', views.my_adoption_requests, name='my_adoption_requests'),
    path('clear-notifications/', views.clear_all_notifications, name='clear_all_notifications'),

]
