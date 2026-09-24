from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace_catalog_view, name='marketplace_catalog'),
    path('product/<int:pk>/', views.product_detail_view, name='marketplace_product_detail'),
    path('group-buying/', views.group_buying_view, name='group_buying_list'),
    path('group-buying/join/<int:pool_id>/', views.join_group_pool_view, name='join_group_pool'),
    path('trace/<str:batch_code>/', views.provenance_passport_by_code_view, name='provenance_passport'),

    # Review URLs
    path('review/submit/', views.submit_review_view, name='submit_review'),
    path('review/thankyou/', views.review_submitted_success_view, name='review_submitted_success'),
    path('review/api/submit/', views.api_submit_review_ajax, name='api_submit_review_ajax'),
]