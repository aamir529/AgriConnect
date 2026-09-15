from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from apps.accounts.decorators import role_required
from apps.orders.models import Order
from apps.farmers.models import FarmerSMSLog
from .models import DeliveryAssignment

@login_required
@role_required(['DELIVERY', 'ADMIN'])
def dispatch_dashboard_view(request):
    """
    Fleet Dispatch Dashboard for Delivery Partners (e.g. Rajesh Verma).
    Shows batch pickups from village aggregation hubs and direct customer doorstep deliveries.
    """
    user = request.user
    
    if user.is_superuser:
        assignments = DeliveryAssignment.objects.all().select_related('order__consumer', 'delivery_person').prefetch_related('order__items__product').order_by('-assigned_at')
    else:
        assignments = DeliveryAssignment.objects.filter(delivery_person=user).select_related('order__consumer').prefetch_related('order__items__product').order_by('-assigned_at')

    # Metrics
    total_assigned = assignments.count()
    pending_pickups = assignments.filter(order__status__in=[Order.Status.PLACED, Order.Status.CONFIRMED]).count()
    in_transit_count = assignments.filter(order__status__in=[Order.Status.IN_TRANSIT, Order.Status.OUT_FOR_DELIVERY]).count()
    delivered_count = assignments.filter(order__status=Order.Status.DELIVERED).count()
    
    # Calculate driver earnings (₹60 base per successful doorstep drop)
    driver_earnings = delivered_count * 60

    # Total payload kg
    total_payload_kg = sum([a.order.total_weight_kg for a in assignments if a.order.status != Order.Status.DELIVERED])

    context = {
        'assignments': assignments,
        'total_assigned': total_assigned,
        'pending_pickups': pending_pickups,
        'in_transit_count': in_transit_count,
        'delivered_count': delivered_count,
        'driver_earnings': driver_earnings,
        'total_payload_kg': total_payload_kg,
    }
    return render(request, 'logistics/dispatch_dashboard.html', context)


@login_required
@role_required(['DELIVERY', 'ADMIN'])
def update_delivery_status_view(request, order_id):
    """
    Advances delivery milestone and dispatches automated simulated SMS alerts to rural growers.
    """
    order = get_object_or_404(Order, id=order_id)
    assignment, _ = DeliveryAssignment.objects.get_or_create(
        order=order,
        defaults={'delivery_person': request.user}
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        driver_name = request.user.get_full_name() or request.user.username

        if action == 'mark_picked_up':
            order.status = Order.Status.IN_TRANSIT
            order.save()
            assignment.mark_picked_up()
            
            # Send SMS to farmers
            notified_farmers = set()
            for item in order.items.all():
                farmer = item.product.farmer
                if farmer.id not in notified_farmers:
                    notified_farmers.add(farmer.id)
                    FarmerSMSLog.objects.create(
                        farmer=farmer,
                        alert_type=FarmerSMSLog.AlertType.PICKUP_DONE,
                        phone_number=farmer.user.phone,
                        message_text=(
                            f"Dispatch Suchna: Fasal (Order #{order.order_number}) "
                            f"Delivery Partner {driver_name} dwara Gram Kendra se utha li gayi hai "
                            f"aur cold van ({assignment.vehicle_number}) se rawana ho gayi hai."
                        )
                    )
            messages.success(request, f"Order #{order.order_number} marked as IN TRANSIT. Farmers notified via SMS.")

        elif action == 'mark_out_for_delivery':
            order.status = Order.Status.OUT_FOR_DELIVERY
            order.save()
            messages.info(request, f"Order #{order.order_number} is now OUT FOR DELIVERY.")

        elif action == 'mark_delivered':
            order.status = Order.Status.DELIVERED
            order.save()
            assignment.mark_delivered()

            # Final delivery SMS alert to farmers
            notified_farmers = set()
            for item in order.items.all():
                farmer = item.product.farmer
                if farmer.id not in notified_farmers:
                    notified_farmers.add(farmer.id)
                    FarmerSMSLog.objects.create(
                        farmer=farmer,
                        alert_type=FarmerSMSLog.AlertType.PAYMENT_REMITTED,
                        phone_number=farmer.user.phone,
                        message_text=(
                            f"Delivery Safal! Order #{order.order_number} grahak ko pahunch gaya hai. "
                            f"Kul kisan rashi Rs {item.farmer_subtotal} aapke khate me jald credit hogi."
                        )
                    )
            messages.success(request, f"Order #{order.order_number} successfully DELIVERED! Customer confirmed.")

    return redirect('dispatch_dashboard')


@login_required
@role_required(['DELIVERY', 'FACILITATOR', 'ADMIN'])
def batch_manifest_view(request):
    """
    Printable aggregation manifest grouping orders ready for bulk pickup at Angara Hub.
    """
    orders = Order.objects.filter(
        status__in=[Order.Status.PLACED, Order.Status.CONFIRMED]
    ).prefetch_related('items__product__farmer__user', 'consumer')

    total_weight = sum([o.total_weight_kg for o in orders])
    total_crates = max(1, int(total_weight / 15)) # ~15kg per crate

    context = {
        'orders': orders,
        'hub_name': 'Angara Digital CSC Aggregation Hub',
        'hub_lead': 'Sunil Mahto',
        'hub_district': 'Ranchi, Jharkhand',
        'total_orders': orders.count(),
        'total_weight': total_weight,
        'total_crates': total_crates,
        'manifest_date': timezone.now(),
    }
    return render(request, 'logistics/batch_manifest.html', context)


@login_required
@role_required(['DELIVERY', 'FACILITATOR', 'ADMIN'])
def iot_telemetry_view(request):
    """
    IoT Cold-Chain Telemetry & Freshness Sensor Monitoring Dashboard.
    Simulates real-time thermal, humidity, and vibration tracking for perishables in transit.
    """
    assignment = DeliveryAssignment.objects.select_related('order', 'delivery_person').first()
    
    telemetry = {
        'vehicle_number': assignment.vehicle_number if assignment else 'JH-01-EF-4921',
        'vehicle_type': assignment.vehicle_type if assignment else 'Tata Ace Insulated Cold Van',
        'driver_name': assignment.delivery_person.get_full_name() if (assignment and assignment.delivery_person) else 'Rajesh Verma',
        'driver_phone': assignment.delivery_person.phone if (assignment and assignment.delivery_person) else '+91 94311 88776',
        'current_temp_c': 12.4,
        'target_temp_c': 12.0,
        'temp_status': 'Optimal (सुरक्षित)',
        'temp_status_color': 'success',
        'relative_humidity_pct': 85.5,
        'humidity_status': 'Optimal Freshness',
        'transit_speed_kmh': 42,
        'vibration_g': 0.18,
        'vibration_status': 'Smooth Highway Transit',
        'cold_chain_compliance_pct': 99.4,
        'active_payload_kg': assignment.order.total_weight_kg if (assignment and assignment.order) else 35.0,
        'origin_hub': 'Angara CSC Rural Aggregation Center',
        'destination': (assignment.order.delivery_address[:35] + '...') if (assignment and assignment.order) else 'Morabadi, Ranchi',
        'battery_level_pct': 94,
        'last_ping_seconds_ago': 4,
    }

    context = {
        'telemetry': telemetry,
        'assignment': assignment,
    }
    return render(request, 'logistics/iot_telemetry.html', context)

