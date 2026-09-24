from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import CustomerReview, GroupBuyingPool
from apps.products.models import Product


def marketplace_catalog_view(request):
    products = Product.objects.filter(is_active=True).select_related('farmer__user', 'category')
    return render(request, 'marketplace/catalog.html', {'products': products})


def group_buying_view(request):
    pools = GroupBuyingPool.objects.all().select_related('product')
    return render(request, 'marketplace/group_buying.html', {'pools': pools})


def join_group_pool_view(request, pool_id):
    pool = get_object_or_404(GroupBuyingPool, pk=pool_id)
    pools = GroupBuyingPool.objects.all().select_related('product')
    pledge_message = None
    if request.method == 'POST':
        pledged_kg = request.POST.get('pledged_kg', '0')
        pledge_message = f"Community Group Buying: Aapka {pledged_kg} kg pledge record ho gaya!"
    return render(request, 'marketplace/group_buying.html', {
        'pool': pool, 'pools': pools, 'pledge_message': pledge_message
    })



def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'marketplace/product_detail.html', {'product': product})


def provenance_passport_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'marketplace/provenance_passport.html', {'product': product})


def provenance_passport_by_code_view(request, batch_code):
    product = Product.objects.first()
    return render(request, 'marketplace/provenance_passport.html', {'product': product, 'batch_code': batch_code})


# ============================================================
# REVIEW VIEWS
# ============================================================

def submit_review_view(request):
    """GET: Show review form. POST: Save review and redirect with success."""
    if request.method == 'POST':
        reviewer_name = request.POST.get('reviewer_name', '').strip()
        reviewer_role = request.POST.get('reviewer_role', 'CONSUMER')
        reviewer_location = request.POST.get('reviewer_location', '').strip()
        review_text = request.POST.get('review_text', '').strip()
        try:
            rating = int(request.POST.get('rating', 5))
            if not (1 <= rating <= 5):
                raise ValueError
        except (ValueError, TypeError):
            rating = 5

        errors = []
        if not reviewer_name:
            errors.append("Aapka naam zaroori hai.")
        if not review_text or len(review_text) < 20:
            errors.append("Review kam se kam 20 characters ka hona chahiye.")
        if not reviewer_location:
            errors.append("Location zaroori hai.")

        if errors:
            return render(request, 'marketplace/submit_review.html', {
                'errors': errors, 'form_data': request.POST,
            })

        review = CustomerReview(
            reviewer_name=reviewer_name,
            reviewer_role=reviewer_role,
            reviewer_location=reviewer_location,
            rating=rating,
            review_text=review_text,
        )
        if request.user.is_authenticated:
            review.user = request.user
        review.save()

        messages.success(request, "Shukriya! Aapka review submit ho gaya. Admin approval ke baad homepage par dikhega.")
        return redirect('review_submitted_success')

    return render(request, 'marketplace/submit_review.html', {})


def review_submitted_success_view(request):
    return render(request, 'marketplace/review_success.html', {})


def api_submit_review_ajax(request):
    """AJAX endpoint for review submission."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    reviewer_name = request.POST.get('reviewer_name', '').strip()
    reviewer_role = request.POST.get('reviewer_role', 'CONSUMER')
    reviewer_location = request.POST.get('reviewer_location', '').strip()
    review_text = request.POST.get('review_text', '').strip()
    try:
        rating = max(1, min(5, int(request.POST.get('rating', 5))))
    except (ValueError, TypeError):
        rating = 5

    if not reviewer_name or not review_text or len(review_text) < 10:
        return JsonResponse({'status': 'error', 'message': 'Naam aur review text zaroori hai.'}, status=400)

    review = CustomerReview(
        reviewer_name=reviewer_name, reviewer_role=reviewer_role,
        reviewer_location=reviewer_location, rating=rating, review_text=review_text,
    )
    if request.user.is_authenticated:
        review.user = request.user
    review.save()

    return JsonResponse({
        'status': 'success',
        'message': 'Shukriya! Aapka review submit ho gaya.',
        'review_id': review.pk,
    })