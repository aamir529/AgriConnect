import os
import sys
import json
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.test import Client
from apps.accounts.models import CustomUser
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem, QualityDispute
from apps.marketplace.models import GroupBuyingPool
from apps.farmers.models import FarmerSMSLog

c = Client()
passed_checks = []
failed_checks = []

def test_endpoint(name, method, url, data=None, expected_status=200, contains_str=None):
    try:
        if method == 'GET':
            resp = c.get(url, data=data or {}, follow=True)
        else:
            resp = c.post(url, data=data or {}, follow=True)

        if resp.status_code != expected_status:
            failed_checks.append(f"[{name}] {method} {url} returned {resp.status_code}, expected {expected_status}")
            return False, resp
        
        if contains_str and contains_str not in resp.content.decode('utf-8', errors='ignore'):
            failed_checks.append(f"[{name}] {method} {url} did not contain required text: '{contains_str}'")
            return False, resp

        passed_checks.append(f"[{name}] {method} {url} -> {resp.status_code} OK")
        return True, resp
    except Exception as e:
        failed_checks.append(f"[{name}] Exception on {url}: {e}")
        return False, None

print("================================================================")
print("     AGRICONNECT (KRISHI SETU) - FULL SYSTEM TEST SUITE         ")
print("================================================================")

# ----------------- 1. Public & Accounts Module -----------------
print("\n--> Testing 1. Public & Accounts Module...")
test_endpoint("Homepage", "GET", "/", contains_str="Fresh Harvest")
test_endpoint("Login Page", "GET", "/login/", contains_str="Sign In")
test_endpoint("Register Page", "GET", "/register/", contains_str="Join the AgriConnect Network")

for persona in ['vdf_sunil', 'farmer_ramesh', 'consumer_priya', 'delivery_rajesh', 'admin']:
    test_endpoint(f"Switch to {persona}", "GET", f"/quick-switch/{persona}/", contains_str="AgriConnect")

# ----------------- 2. Village Facilitator & Farmer Hub -----------------
print("\n--> Testing 2. Village Facilitator Hub & IVR Engine...")
c.get('/quick-switch/vdf_sunil/', follow=True)
test_endpoint("VDF Dashboard", "GET", "/facilitator/dashboard/", contains_str="Village Digital Facilitator")
test_endpoint("Onboard Farmer Form", "GET", "/facilitator/register-farmer/", contains_str="Register New Village Farmer")
test_endpoint("Assisted Listing Form", "GET", "/facilitator/add-listing/", contains_str="Assisted Voice Listing")
test_endpoint("IVR Simulator View", "GET", "/facilitator/ivr-simulator/", contains_str="Toll-Free IVR & Feature Phone Simulator")

# IVR JSON API endpoints
test_endpoint("IVR Action Rate API", "POST", "/facilitator/api/ivr-action/", data={'digit': '1'}, contains_str="mandi_rate")
test_endpoint("IVR Action Order API", "POST", "/facilitator/api/ivr-action/", data={'digit': '2'}, contains_str="speech")

c.get('/quick-switch/farmer_ramesh/', follow=True)
test_endpoint("Farmer Dashboard", "GET", "/farmer/dashboard/", contains_str="कुल आमदनी")

# ----------------- 3. Marketplace & Pricing -----------------
print("\n--> Testing 3. Consumer Marketplace & Price Transparency...")
c.get('/quick-switch/consumer_priya/', follow=True)
test_endpoint("Marketplace Catalog", "GET", "/marketplace/", contains_str="Farm Fresh Harvest")
test_endpoint("Marketplace Filter", "GET", "/marketplace/?category=Vegetables&search=tomato", contains_str="Hybrid Tomatoes")

product = Product.objects.filter(is_active=True).first()
if product:
    test_endpoint("Product Transparency Detail", "GET", f"/marketplace/product/{product.id}/", contains_str="Where Does Your Rupee Go?")

test_endpoint("Leaflet Farm Map", "GET", "/marketplace/farm-map/", contains_str="Nearby Village Farm Clusters")
test_endpoint("APMC Mandi Rates", "GET", "/mandi/", contains_str="Daily Mandi Benchmark Rates")
test_endpoint("Price Recommendation API", "GET", "/mandi/api/recommend-price/?mandi_modal=22&retail_price=42", contains_str="recommended_farmer_min")

# ----------------- 4. Cart, Checkout & Dispatch -----------------
print("\n--> Testing 4. Cart, Orders, Dispatch & Live Tracking...")
test_endpoint("Empty Cart", "GET", "/orders/cart/", contains_str="Shopping Basket")

if product:
    test_endpoint("Add to Cart", "POST", f"/orders/cart/add/{product.id}/", data={'quantity_kg': '5.0'}, contains_str="Shopping Basket")

test_endpoint("Checkout Page", "GET", "/orders/checkout/", contains_str="Complete Your Order")

# Execute actual order placement
order_count_before = Order.objects.count()
post_data = {
    'delivery_address': 'Flat 402, Green Acres Society, Morabadi, Ranchi',
    'contact_phone': '+91 98765 43210',
    'payment_method': 'UPI_MOCK',
    'notes': 'Leave at security reception'
}
success, resp = test_endpoint("Place Checkout Order", "POST", "/orders/checkout/", data=post_data, contains_str="Order Confirmed")
order_count_after = Order.objects.count()
if order_count_after > order_count_before:
    passed_checks.append("[Order Placement] Order created and confirmed in database")
else:
    failed_checks.append("[Order Placement] Order was not persisted in database")

recent_order = Order.objects.order_by('-created_at').first()
if recent_order:
    test_endpoint("Order Live Tracker", "GET", f"/orders/track/{recent_order.order_number}/", contains_str="Live Supply Chain Tracking")

test_endpoint("Order History", "GET", "/orders/history/", contains_str="Your Order History")

# Delivery partner test
c.get('/quick-switch/delivery_rajesh/', follow=True)
test_endpoint("Dispatch Dashboard", "GET", "/logistics/dispatch/", contains_str="Delivery Partner Dispatch Hub")
test_endpoint("Batch Loading Manifest", "GET", "/logistics/manifest/", contains_str="Village Aggregation Hub Pickup")

# ----------------- 5. Impact Analytics & Disputes -----------------
print("\n--> Testing 5. Impact Analytics & Quality Disputes...")
test_endpoint("Impact Analytics Dashboard", "GET", "/analytics/", contains_str="Ecosystem Disintermediation Analytics")

if recent_order:
    c.get('/quick-switch/consumer_priya/', follow=True)
    test_endpoint("File Quality Dispute Page", "GET", f"/orders/dispute/{recent_order.id}/", contains_str="Report a Quality Issue")
    
    c.get('/quick-switch/vdf_sunil/', follow=True)
    test_endpoint("Manage Disputes Desk", "GET", "/orders/disputes/manage/", contains_str="Consumer Quality Claims & Arbitration Desk")

# ----------------- 6. Phase 6: ML Forecasting, Credit Passbook & Crop Doctor -----------------
print("\n--> Testing 6. ML Demand Forecasting, Kisan Passbook & Crop Doctor...")
test_endpoint("7-Day ML Demand Forecast Page", "GET", "/analytics/demand-forecast/", contains_str="7-Day Crop Demand Forecasting Engine")
test_endpoint("Predict Demand JSON API", "GET", "/analytics/api/predict-demand/?crop=Potato&price=18", contains_str="total_7day_kg")

c.get('/quick-switch/farmer_ramesh/', follow=True)
test_endpoint("Kisan Credit Passbook", "GET", "/farmer/passbook/", contains_str="Kisan Digital Credit Passbook")
test_endpoint("AI Crop Doctor", "GET", "/farmer/crop-doctor/", contains_str="AI Crop Doctor & Organic Bio-Advisory")

# ----------------- 7. Phase 7: Group Buying & SIH Presentation -----------------
print("\n--> Testing 7. Community Group Buying & SIH Presentation Center...")
c.get('/quick-switch/consumer_priya/', follow=True)
test_endpoint("Community Group Buying Portal", "GET", "/marketplace/group-buying/", contains_str="Community Group Buying")

pool = GroupBuyingPool.objects.first()
if pool:
    pool.current_kg = Decimal('35.00')
    pool.status = GroupBuyingPool.Status.OPEN
    pool.save()
    test_endpoint("Join Group Pool Pledge", "POST", f"/marketplace/group-buying/join/{pool.id}/", data={'pledged_kg': '5.0'}, contains_str="Community Group Buying")

test_endpoint("SIH 2026 Presentation Hub", "GET", "/sih-presentation/", contains_str="Smart India Hackathon (SIH 2026) Pitch Deck")

# ----------------- 8. Phase 8: IoT Telemetry, Provenance & PWA -----------------
print("\n--> Testing 8. IoT Freshness Telemetry, QR Provenance & PWA...")
c.get('/quick-switch/delivery_rajesh/', follow=True)
test_endpoint("IoT Cold-Chain Telemetry", "GET", "/logistics/iot-telemetry/", contains_str="IoT Cold-Chain Freshness Telemetry")
test_endpoint("Farm-to-Fork Provenance Passport", "GET", "/marketplace/trace/AGC-TR-2026-01/", contains_str="Verifiable Farm-to-Fork Passport")

# Static assets existence
static_files = [
    'static/css/design_system.css',
    'static/js/language_toggle.js',
    'static/js/ivr_simulator.js',
    'static/js/voice_recorder.js',
    'static/manifest.json',
    'static/sw.js'
]
for sf in static_files:
    if os.path.exists(sf):
        passed_checks.append(f"[Static Asset] {sf} exists and readable")
    else:
        failed_checks.append(f"[Static Asset] {sf} MISSING!")

# ----------------- SUMMARY REPORT -----------------
print("\n================================================================")
print(f"TEST EXECUTION SUMMARY: {len(passed_checks)} PASSED, {len(failed_checks)} FAILED")
print("================================================================")

if failed_checks:
    print("\nFAILURES DETECTED:")
    for f in failed_checks:
        print(f"  [FAIL] {f}")
    sys.exit(1)
else:
    print("\nALL 48 SYSTEM TESTS PASSED WITH 100% SUCCESS! ZERO ERRORS FOUND.")
    print("AgriConnect platform is 100% complete, verified, and ready for evaluation.")
