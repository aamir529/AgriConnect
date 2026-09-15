from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal

from apps.products.models import Product
from apps.farmers.models import FarmerSMSLog
from .models import Order, OrderItem, QualityDispute
from .cart import Cart

def cart_detail_view(request):
    cart = Cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})


def add_to_cart_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    quantity = request.POST.get('quantity_kg', product.minimum_order_kg)
    try:
        qty = float(quantity)
        if qty <= 0:
            qty = float(product.minimum_order_kg)
    except (ValueError, TypeError):
        qty = float(product.minimum_order_kg)

    if qty > float(product.available_quantity_kg):
        messages.error(request, f"Sorry, only {product.available_quantity_kg} kg available for {product.name}.")
        return redirect('marketplace_product_detail', pk=product.id)

    cart.add(product, quantity_kg=qty)
    messages.success(request, f"Added {qty} kg of {product.name} to your basket!")
    
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('cart_detail')


def update_cart_quantity_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    new_qty = request.POST.get('quantity_kg', 1.0)
    try:
        qty = float(new_qty)
    except (ValueError, TypeError):
        qty = 1.0

    if qty > float(product.available_quantity_kg):
        messages.warning(request, f"Requested quantity adjusted to maximum available stock ({product.available_quantity_kg} kg).")
        qty = float(product.available_quantity_kg)

    cart.set_quantity(product, qty)
    messages.info(request, f"Updated quantity for {product.name}.")
    return redirect('cart_detail')


def remove_from_cart_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from your basket.")
    return redirect('cart_detail')


@login_required
def checkout_view(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your basket is empty. Please add farm produce before checking out.")
        return redirect('marketplace_catalog')

    user = request.user

    if request.method == 'POST':
        address = request.POST.get('delivery_address', '').strip()
        phone = request.POST.get('contact_phone', '').strip()
        payment_method = request.POST.get('payment_method', 'UPI_MOCK')

        if not address or not phone:
            messages.error(request, "Please provide a valid delivery address and contact phone number.")
            return render(request, 'orders/checkout.html', {'cart': cart})

        # Calculate totals
        total_amount = Decimal(str(cart.get_total()))
        farmer_total = Decimal(str(cart.get_farmer_total()))
        delivery_fee = Decimal(str(cart.get_delivery_fee()))

        # Create Order
        order = Order.objects.create(
            consumer=user,
            total_amount=total_amount,
            farmer_payout_amount=farmer_total,
            delivery_fee=delivery_fee,
            delivery_address=address,
            contact_phone=phone,
            payment_method=payment_method,
            status=Order.Status.PLACED,
            is_paid=True
        )

        # Create OrderItems and deduct stock
        notified_farmers = set()
        for item in cart:
            product = item['product']
            qty = Decimal(str(item['quantity']))
            price = Decimal(str(item['price']))
            farmer_price = Decimal(str(item['farmer_price']))
            subtotal = Decimal(str(item['total_price']))
            farmer_sub = Decimal(str(item['farmer_subtotal']))

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity_kg=qty,
                price_per_kg=price,
                farmer_price_per_kg=farmer_price,
                subtotal=subtotal,
                farmer_subtotal=farmer_sub
            )

            # Deduct stock
            product.available_quantity_kg = max(Decimal('0.00'), product.available_quantity_kg - qty)
            if product.available_quantity_kg == 0:
                product.is_active = False
            product.save()

            # Record Simulated SMS alert to each affected Farmer
            farmer_profile = product.farmer
            if farmer_profile.id not in notified_farmers:
                notified_farmers.add(farmer_profile.id)
                FarmerSMSLog.objects.create(
                    farmer=farmer_profile,
                    alert_type=FarmerSMSLog.AlertType.ORDER_RECEIVED,
                    phone_number=farmer_profile.user.phone,
                    message_text=(
                        f"Naya Order Prapt! Aapke {product.name} ka order prapt hua hai. "
                        f"Order #{order.order_number}. Kul bhugtan: Rs {farmer_sub}. "
                        f"Kripya fasal Gram Kendra me taiyar rakhein."
                    )
                )

        # Clear the session cart
        cart.clear()
        messages.success(request, f"Order #{order.order_number} placed successfully!")
        return redirect('order_success', order_id=order.id)

    initial_address = user.address or f"{user.village_or_city or ''}, {user.district or ''}"
    initial_phone = user.phone or ''

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'initial_address': initial_address,
        'initial_phone': initial_phone,
    })


@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history_view(request):
    orders = Order.objects.filter(consumer=request.user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


def live_tracking_view(request, order_number):
    """
    Public / Authenticated real-time delivery milestone tracker for a given order.
    """
    order = get_object_or_404(Order.objects.prefetch_related('items__product__farmer__user'), order_number=order_number)
    
    # Milestone mapping
    status_steps = [
        ('PLACED', 'Order Placed', 'Confirmed digitally by system', 'fa-receipt'),
        ('CONFIRMED', 'Aggregated at Village Hub', 'Quality checked by VDF Sunil Mahto', 'fa-boxes-packing'),
        ('IN_TRANSIT', 'In Cold Chain Transit', 'Dispatched in Tata Ace Mini-Van', 'fa-truck-fast'),
        ('OUT_FOR_DELIVERY', 'Out for Doorstep Drop', 'Local courier arriving at destination', 'fa-motorcycle'),
        ('DELIVERED', 'Delivered Safely', 'Produce handed over to consumer', 'fa-circle-check'),
    ]

    status_keys = [s[0] for s in status_steps]
    current_index = 0
    if order.status in status_keys:
        current_index = status_keys.index(order.status)

    milestones = []
    for idx, (code, title, desc, icon) in enumerate(status_steps):
        is_completed = idx < current_index
        is_active = idx == current_index
        milestones.append({
            'code': code,
            'title': title,
            'desc': desc,
            'icon': icon,
            'is_completed': is_completed,
            'is_active': is_active,
        })

    # Assignment info if present
    assignment = getattr(order, 'delivery_assignment', None)

    context = {
        'order': order,
        'milestones': milestones,
        'assignment': assignment,
        'current_index': current_index,
    }
    return render(request, 'orders/tracking.html', context)


@login_required
def file_dispute_view(request, order_id):
    """
    Consumer portal to lodge a quality assurance / damaged produce claim.
    """
    order = get_object_or_404(Order, id=order_id, consumer=request.user)
    
    if request.method == 'POST':
        item_id = request.POST.get('order_item_id')
        issue_type = request.POST.get('issue_type', QualityDispute.IssueType.SPOILED_TRANSIT)
        description = request.POST.get('description', '').strip()
        refund_amount = request.POST.get('refund_amount_requested', '0.00')

        try:
            amt = Decimal(refund_amount)
        except:
            amt = Decimal('0.00')

        item = None
        if item_id:
            item = OrderItem.objects.filter(id=item_id, order=order).first()

        dispute = QualityDispute.objects.create(
            order=order,
            consumer=request.user,
            order_item=item,
            issue_type=issue_type,
            description=description,
            refund_amount_requested=amt,
            status=QualityDispute.Status.PENDING
        )
        messages.success(request, f"Quality claim #{dispute.id} submitted. The village hub facilitator will inspect and process your refund.")
        return redirect('order_history')

    context = {
        'order': order,
        'issue_types': QualityDispute.IssueType.choices,
    }
    return render(request, 'orders/file_dispute.html', context)


@login_required
def disputes_manage_view(request):
    """
    Facilitator & Admin portal to review and arbitrate consumer quality claims.
    """
    if not (request.user.is_facilitator or request.user.is_superuser):
        messages.error(request, "Access restricted to Village Facilitators and Platform Admins.")
        return redirect('home')

    disputes = QualityDispute.objects.select_related('order', 'consumer', 'order_item__product').order_by('-created_at')
    
    pending_count = disputes.filter(status=QualityDispute.Status.PENDING).count()
    resolved_count = disputes.filter(status=QualityDispute.Status.RESOLVED_REFUNDED).count()

    context = {
        'disputes': disputes,
        'pending_count': pending_count,
        'resolved_count': resolved_count,
    }
    return render(request, 'orders/disputes_manage.html', context)


@login_required
def resolve_dispute_view(request, dispute_id):
    """
    Action endpoint to approve or reject a dispute claim.
    """
    if not (request.user.is_facilitator or request.user.is_superuser):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    dispute = get_object_or_404(QualityDispute, id=dispute_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('resolution_notes', '').strip()

        if action == 'approve':
            dispute.resolve(is_approved=True, notes=notes or "Approved by VDF Hub Inspector. Refund credited.")
            messages.success(request, f"Claim #{dispute.id} APPROVED. Refund of Rs {dispute.refund_amount_requested} credited to {dispute.consumer.get_full_name()}.")
        elif action == 'reject':
            dispute.resolve(is_approved=False, notes=notes or "Inspected batch logs. Spoilage outside transit timeline.")
            messages.warning(request, f"Claim #{dispute.id} marked as REJECTED.")

    return redirect('disputes_manage')


