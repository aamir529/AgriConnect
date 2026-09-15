from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public Home View
    path('', home_view, name='home'),

    # Accounts & Authentication
    path('accounts/', include('apps.accounts.urls')),

    # Phase 2: Facilitator & Farmer Hubs
    path('facilitator/', include('apps.facilitators.urls')),
    path('farmer/', include('apps.farmers.urls')),

    # Phase 3: Marketplace, Orders & Mandi Prices
    path('marketplace/', include('apps.marketplace.urls')),
    path('orders/', include('apps.orders.urls')),
    path('mandi/', include('apps.market_intelligence.urls')),

    # Phase 4: Logistics & Dispatch Fleet
    path('logistics/', include('apps.logistics.urls')),

    # Phase 5: Impact Analytics
    path('analytics/', include('apps.analytics.urls')),
]

# Quick URL shortcuts at root level
from apps.accounts import views as account_views
urlpatterns += [
    path('login/', account_views.login_view, name='login'),
    path('register/', account_views.register_view, name='register'),
    path('logout/', account_views.logout_view, name='logout'),
    path('dashboard/', account_views.dashboard_router_view, name='dashboard_router'),
    path('profile/', account_views.profile_view, name='profile'),
    path('quick-switch/<str:username>/', account_views.quick_switch_user_view, name='quick_switch_user'),
]

from apps.analytics import views as analytics_views
urlpatterns += [
    path('sih-presentation/', analytics_views.sih_presentation_view, name='sih_presentation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
