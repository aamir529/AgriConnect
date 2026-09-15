from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_router_view, name='dashboard_router'),
    path('profile/', views.profile_view, name='profile'),
    path('quick-switch/<str:username>/', views.quick_switch_user_view, name='quick_switch_user'),
]
