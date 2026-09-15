from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity_view, name='update_cart_quantity'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('history/', views.order_history_view, name='order_history'),
    path('track/<str:order_number>/', views.live_tracking_view, name='live_tracking'),
    path('dispute/<int:order_id>/', views.file_dispute_view, name='file_dispute'),
    path('disputes/manage/', views.disputes_manage_view, name='disputes_manage'),
    path('disputes/resolve/<int:dispute_id>/', views.resolve_dispute_view, name='resolve_dispute'),
]
