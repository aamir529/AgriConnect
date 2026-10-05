from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import CustomerReview, GroupBuyingPool, GroupBuyingParticipant
from apps.products.models import Product


def marketplace_catalog_view(request):
    products = Product.objects.filter(is_active=True).select_related('farmer__user', 'category')
    return render(request, 'marketplace/catalog.html', {'products': products})


def group_buying_view(request):
    pools = GroupBuyingPool.objects.all().select_related(
        'product__farmer__user',
        'product__category'
    ).order_by('-created_at')
    return render(request, 'marketplace/group_buying.html', {'pools': pools})


def join_group_pool_view(request, pool_id):
    pool = get_object_or_404(GroupBuyingPool, pk=pool_id)
    
    if request.method == 'POST':
        # 1. Check user authentication
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to pledge and join this neighborhood bulk buying pool.")
            return redirect(f"/accounts/login/?next=/marketplace/group-buying/")
        
        # 2. Check pool status
        if pool.status != GroupBuyingPool.Status.OPEN:
            messages.error(request, f"Pledging is closed for '{pool.title}' ({pool.get_status_display()}).")
            return redirect('group_buying_list')
        
        # 3. Validate pledge quantity
        raw_qty = request.POST.get('pledged_kg', '5.0')
        try:
            pledged_kg = Decimal(str(raw_qty)).quantize(Decimal('0.01'))
            if pledged_kg <= Decimal('0.00'):
                raise ValueError
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, "Invalid pledge quantity selected. Please choose a valid weight.")
            return redirect('group_buying_list')
        
        # 4. Check remaining capacity
        remaining = Decimal(str(pool.remaining_kg))
        if pledged_kg > remaining:
            messages.warning(
                request,
                f"Requested {pledged_kg} kg exceeds the remaining pool quota. "
                f"Only {remaining} kg is needed to complete this pool."
            )
            return redirect('group_buying_list')
        
        # 5. Record participant pledge
        GroupBuyingParticipant.objects.create(
            pool=pool,
            consumer=request.user,
            pledged_kg=pledged_kg,
            status=GroupBuyingParticipant.Status.PLEDGED
        )
        
        # 6. Update current pledged kg and lock if target fulfilled
        pool.current_kg = (pool.current_kg + pledged_kg).quantize(Decimal('0.01'))
        if pool.current_kg >= pool.target_kg:
            pool.current_kg = pool.target_kg
            pool.status = GroupBuyingPool.Status.LOCKED_FULL
        pool.save()
        
        total_pledge_cost = (pledged_kg * pool.bulk_price_per_kg).quantize(Decimal('0.01'))
        messages.success(
            request,
            f"🎉 Success! Pledged {pledged_kg} kg (₹{total_pledge_cost}) for '{pool.title}'. "
            f"Your order is locked for consolidated delivery to {pool.apartment_cluster}."
        )
    
    return redirect('group_buying_list')



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