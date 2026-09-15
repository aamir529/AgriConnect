# Product Requirements Document (PRD) & Django Technical Blueprint

## Project Title
**AgriConnect – Transparent Digital Agricultural Supply Chain Platform with Assisted-Digital Access**

---

# Part I: Product Requirements Document (PRD)

## 1. Product Overview

### Product Name
**AgriConnect – Transparent Digital Agricultural Supply Chain Platform**

### Product Type
Full-stack web platform with analytics, marketplace, assisted farmer services, and optional ML-based demand forecasting.

### Recommended Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5 / TailwindCSS |
| **Backend** | Python 3.11+, Django 5.x, Django REST Framework (DRF) |
| **Database** | PostgreSQL (Development/Production), SQLite (Rapid testing) |
| **Data Analytics** | Pandas, NumPy, Matplotlib / Plotly / Chart.js |
| **Machine Learning** | Scikit-learn |
| **Maps & Geo** | Leaflet.js + OpenStreetMap |
| **Version Control** | Git + GitHub |

---

## 2. Problem Statement

Traditional agricultural supply chains involve multiple intermediaries:

$$\text{Farmer} \longrightarrow \text{Local Trader} \longrightarrow \text{Wholesaler} \longrightarrow \text{Distributor} \longrightarrow \text{Retailer} \longrightarrow \text{Consumer}$$

This results in farmers receiving a drastically lower share of the final consumer value (often only 20%–30%) while consumers pay an inflated price. AgriConnect reduces unnecessary intermediaries and makes the price chain visible and transparent.

### Additional Problem: The Digital Literacy Gap
Conventional farmer marketplaces assume that all farmers:
* Own modern smartphones
* Have reliable high-speed internet access
* Are comfortable operating complex mobile apps
* Can chat in English and negotiate with online buyers
* Can manage digital logistics and tracking screens

AgriConnect specifically resolves this digital-literacy hurdle through an **assisted-digital ("phygital") model**.

---

## 3. Product Vision

> **"To connect farmers directly with consumers and buyers while improving farmer earnings, providing transparent agricultural pricing, and making digital agricultural services accessible even to farmers with limited digital literacy."**

---

## 4. Product Goals

1. **Reduce Intermediaries:** Disintermediate multi-layered middleman chains.
2. **Improve Farmer Realization:** Increase farmer take-home pay from ~25% to 65%–75% of final retail value.
3. **Price Transparency:** Provide full visibility into supply-chain price decomposition.
4. **Direct Connectivity:** Enable direct commercial interactions between farmer hubs and consumers/RWAs.
5. **Local Market Benchmarks:** Aggregate and display daily mandi/APMC price data.
6. **Support Low-Literacy Farmers:** Provide access via Village Digital Facilitators (VDF), IVR, and SMS.
7. **Streamlined Fulfillment:** Aggregate village-level harvests for efficient urban bulk deliveries.
8. **Fair Price Guidance:** Provide data-driven price recommendations to prevent distress selling.
9. **Supply Chain Margin Analytics:** Expose margins, logistics costs, and consumer savings dynamically.
10. **Demand Forecasting:** Use historical trends and machine learning to project 7-day crop demand.

---

## 5. Target Users & Stakeholders

The platform serves **five primary user roles**:

### 5.1 Farmer
* Minimal digital interaction required.
* Registered via a Village Digital Facilitator (VDF) or IVR.
* Provides produce availability and quantity.
* Views or hears recommended price vs. local mandi rates.
* Receives order notifications and payment confirmations via SMS / UPI.

### 5.2 Village Digital Facilitator (VDF)
* A trained local person (e.g., rural youth, CSC operator, or local merchant) operating on behalf of 50–100 local farmers.
* Onboards farmers and manages farmer profiles.
* Creates produce listings (crop type, quantity, harvest date, expected price, photos).
* Assists farmers with order aggregation, weighing, and delivery handoffs.
* Accesses the platform via a responsive web portal / PWA.

### 5.3 Consumer / Buyer
* Urban households, residential welfare associations (RWAs), and institutional buyers.
* Searches and filters produce by crop, locality, price, and freshness.
* Views price comparison tables and supply-chain margin breakdowns.
* Adds items to cart, places orders, pays online, and tracks delivery status.
* Submits ratings and reviews upon delivery.

### 5.4 Delivery Partner
* Local logistics coordinators and tempo/van drivers.
* Views assigned batch pickups from village VDF aggregation hubs.
* Updates milestone delivery statuses (`Pickup Scheduled`, `Picked Up`, `Out for Delivery`, `Delivered`).

### 5.5 Admin
* Superusers, platform operations staff, or cooperative managers.
* Manages users, farmers, facilitators, produce categories, and complaints.
* Monitors market prices, system revenues, and consumer savings.
* Reviews analytical dashboards and ML demand predictions.

---

## 6. Assisted-Digital Model Workflow

Rather than forcing farmers to operate an e-commerce app:

```text
                 ┌── Village Digital Facilitator (VDF)
Farmer ──────────┼── IVR / Phone Menu (Mocked/Simulated)
                 └── SMS / Voice Input
                         ↓
              AgriConnect Platform
                         ↓
           Buyer / Logistics / Analytics
```

### Scenario: A farmer has 500 kg of tomatoes
1. **Communication:** Farmer informs local facilitator: *"Mere paas 500 kilo hybrid tamatar hai."*
2. **Data Entry:** Facilitator opens VDF portal, selects farmer, enters crop (Tomato), quantity (500 kg), harvest date, and expected price (₹28/kg).
3. **Price Check:** Platform fetches local mandi benchmark (e.g., ₹24/kg) and retail average (₹40/kg).
4. **Fair Price Recommendation:** System suggests listing range: **₹26 – ₹30/kg**.
5. **Listing Published:** Produce is immediately visible on consumer marketplace.
6. **Notification:** Farmer receives SMS: *"Aapke 500 kg tamatar platform par darj ho gaye hain."*

---

## 7. Price Transparency & Margin Decomposition

The core innovation is breaking down how consumer expenditure is distributed:

### Illustrative Supply Chain Comparison

| Supply Chain Stage | Traditional Market | AgriConnect Direct Platform |
| :--- | :--- | :--- |
| **Farmer Realization** | ₹20 / kg | **₹28 / kg (+40% to Farmer)** |
| **Local Trader Margin** | ₹5 / kg | ₹0 / kg |
| **Wholesaler Margin** | ₹7 / kg | ₹0 / kg |
| **Facilitator & QC Fee** | — | ₹1.50 / kg |
| **Logistics & Packaging** | — | ₹3.50 / kg |
| **Platform Fee** | — | ₹1.00 / kg |
| **Retailer Markup** | ₹8 / kg | ₹0 / kg |
| **Final Consumer Price** | **₹40 / kg** | **₹34 / kg (-15% Consumer Saving)** |

Every consumer listing displays an interactive **Transparency Breakdown Card** illustrating exact rupee allocations.

---

## 8. Market Price & Fair Price Recommendation Engine

* **Market Price Tracker:** Scrapes / feeds daily modal prices for benchmark crops across nearby APMC mandis.
* **Price Recommendation Logic:**
  $$\text{Recommended Min} = \max(\text{Mandi Modal Price}, \text{Cost of Cultivation} \times 1.2)$$
  $$\text{Recommended Max} = \text{Local Retail Price} \times 0.85$$
* Prevents distress sales during glut periods and flags predatory pricing.

---

## 9. Machine Learning Demand Forecasting

* **Input Features:** Crop type, harvest seasonality, historical order volume, city/district, day of week, price per kg.
* **Algorithms:** Scikit-Learn (Random Forest Regressor / Ridge Regression).
* **Output:** Estimated 7-day demand volume and status indicator (`LOW`, `MODERATE`, `HIGH`, `PEAK`).
* **Implementation Strategy:** Start with rule-based synthetic demand signals, followed by Scikit-Learn model training on order logs.

---

## 10. Geo-Location & Radius Search

* Integrated **Leaflet.js + OpenStreetMap** widget.
* Consumers can filter listings within 10 km, 25 km, or 50 km radii from their location.
* Displays farm cluster pins and estimated pickup-to-drop transit times.

---

## 11. Order & Fulfillment Lifecycle

```text
[Order Placed] 
      ↓
[Farmer/VDF Confirmed] 
      ↓
[Aggregated at VDF Hub] 
      ↓
[Assigned to Delivery Partner] 
      ↓
[Picked Up & Out for Delivery] 
      ↓
[Delivered to Consumer] 
      ↓
[Farmer Payout & Review]
```

---

## 12. Admin KPI Dashboard Metrics

* **Registered Farmers:** Dynamic count
* **Active Facilitators:** Dynamic count
* **Total Produce Listed vs. Sold (kg)**
* **Cumulative Farmer Revenue (₹)**
* **Cumulative Consumer Savings (₹)**
* **Visual Charts:**
  1. Top demanded crops by volume
  2. Average price trend vs. APMC mandi rate
  3. Delivery fulfillment turnaround times
  4. Regional demand heatmaps

---

# Part II: Complete Django Technical & Development Blueprint

---

## 13. System Architecture & Folder Structure

```text
agriconnect_project/
│
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
├── db.sqlite3 (or PostgreSQL configs)
│
├── agriconnect/                   # Project Root Configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/                  # Custom User, Auth, Roles, Profiles
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── decorators.py
│   │   └── serializers.py
│   │
│   ├── farmers/                   # Farm profiles, Voice/SMS intake, Payouts
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── facilitators/              # VDF portal, Farmer registration, Assisted listings
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   │
│   ├── products/                  # Produce catalog, Categories, Quality grading
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── serializers.py
│   │
│   ├── marketplace/               # Consumer browsing, Leaflet map, Transparency widget
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── orders/                    # Cart, Checkout, Order Items, Invoicing
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   │
│   ├── logistics/                 # Deliveries, Dispatch sheets, Tracking
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── market_intelligence/       # Mandi prices, Margin analysis, Price guidance
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── price_engine.py
│   │
│   └── analytics/                 # Admin KPI dashboards, Scikit-learn demand ML
│       ├── views.py
│       ├── urls.py
│       └── ml_models/
│           ├── demand_predictor.py
│           └── train_model.py
│
├── static/
│   ├── css/
│   │   ├── style.css              # Custom styling, glassmorphism, badges
│   │   └── dashboard.css
│   ├── js/
│   │   ├── main.js
│   │   ├── voice_input.js         # Web Speech API for Hindi/English voice input
│   │   ├── map_search.js          # Leaflet.js radius and farmer markers
│   │   ├── price_breakdown.js     # Live calculation of price transparency
│   │   └── ivr_simulator.js       # Interactive DTMF IVR simulator
│   └── images/
│
└── templates/
    ├── base.html                  # Master navbar, footer, alerts
    ├── accounts/
    │   ├── login.html
    │   ├── register.html
    │   └── profile.html
    ├── public/
    │   ├── home.html
    │   ├── about.html
    │   └── how_it_works.html
    ├── facilitator/
    │   ├── dashboard.html
    │   ├── register_farmer.html
    │   ├── add_listing.html
    │   └── ivr_voice_intake.html
    ├── farmer/
    │   ├── dashboard.html
    │   └── my_produce.html
    ├── marketplace/
    │   ├── catalog.html
    │   ├── product_detail.html    # Contains Price Transparency Breakdown
    │   ├── cart.html
    │   └── checkout.html
    ├── orders/
    │   ├── order_success.html
    │   ├── order_detail.html
    │   └── tracking.html
    ├── logistics/
    │   └── dispatch_dashboard.html
    └── analytics/
        ├── admin_dashboard.html   # KPI cards, charts, margin visualizer
        └── demand_forecast.html
```

---

## 14. Authentication, Roles & Permissions

### Role Definitions (`Role` Enum)
* `FARMER`
* `FACILITATOR`
* `CONSUMER`
* `DELIVERY_PARTNER`
* `ADMIN`

### Role-Based Access Control Implementation
Use custom Django decorators to enforce view permissions:

```python
# apps/accounts/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('login')
            if request.user.role not in allowed_roles and not request.user.is_superuser:
                messages.error(request, "Unauthorized access for your account role.")
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
```

---

## 15. Detailed Database Models & Schemas

### 15.1 `apps/accounts/models.py`
```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        FARMER = 'FARMER', 'Farmer'
        FACILITATOR = 'FACILITATOR', 'Village Digital Facilitator'
        CONSUMER = 'CONSUMER', 'Consumer / Buyer'
        DELIVERY = 'DELIVERY', 'Delivery Partner'
        ADMIN = 'ADMIN', 'Platform Administrator'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CONSUMER)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    village_or_city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    preferred_language = models.CharField(max_length=20, default='Hindi')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
```

### 15.2 `apps/facilitators/models.py` & `apps/farmers/models.py`
```python
from django.db import models
from django.conf import settings

class FacilitatorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='facilitator_profile')
    village_name = models.CharField(max_length=120)
    center_name = models.CharField(max_length=150, help_text="CSC center or aggregation hub name")
    assigned_district = models.CharField(max_length=100)
    commission_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=5.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.village_name}"

class FarmerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farmer_profile')
    facilitator = models.ForeignKey(FacilitatorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='farmers')
    land_area_acres = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    primary_crops = models.CharField(max_length=255, help_text="Comma-separated e.g. Tomato, Potato, Onion")
    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    bank_ifsc = models.CharField(max_length=20, blank=True, null=True)
    upi_id = models.CharField(max_length=60, blank=True, null=True)
    is_assisted_only = models.BooleanField(default=True, help_text="True if farmer relies on VDF/IVR")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.user.village_or_city})"
```

### 15.3 `apps/products/models.py`
```python
from django.db import models
from apps.farmers.models import FarmerProfile

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    icon = models.CharField(max_length=50, default="fa-carrot")
    is_perishable = models.BooleanField(default=True)
    shelf_life_days = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name

class Product(models.Model):
    class QualityGrade(models.TextChoices):
        GRADE_A = 'A', 'Grade A (Premium / Export Quality)'
        GRADE_B = 'B', 'Grade B (Standard Market Quality)'
        GRADE_C = 'C', 'Grade C (Processing / Bulk Grade)'

    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=120)
    variety = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    grade = models.CharField(max_length=2, choices=QualityGrade.choices, default=QualityGrade.GRADE_B)
    
    # Quantities & Pricing
    available_quantity_kg = models.DecimalField(max_digits=8, decimal_places=2)
    minimum_order_kg = models.DecimalField(max_digits=6, decimal_places=2, default=5.0)
    farmer_base_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    consumer_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2, help_text="Computed: base + logistics + platform margin")
    
    # Metadata
    harvest_date = models.DateField()
    image = models.ImageField(upload_to='produce_images/', null=True, blank=True)
    is_organic = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_price_breakdown(self):
        """Returns supply chain cost allocation in Rupees."""
        base = float(self.farmer_base_price_per_kg)
        vdf_cut = round(base * 0.05, 2)
        logistics = round(base * 0.10, 2)
        platform_fee = round(base * 0.05, 2)
        total = round(base + vdf_cut + logistics + platform_fee, 2)
        return {
            'farmer_share': base,
            'facilitator_fee': vdf_cut,
            'logistics_fee': logistics,
            'platform_fee': platform_fee,
            'total_consumer_price': total
        }

    def __str__(self):
        return f"{self.name} ({self.farmer.user.village_or_city}) - ₹{self.consumer_price_per_kg}/kg"
```

### 15.4 `apps/orders/models.py` & `apps/logistics/models.py`
```python
from django.db import models
from django.conf import settings
from apps.products.Product import Product

class Order(models.Model):
    class Status(models.TextChoices):
        PLACED = 'PLACED', 'Order Placed'
        CONFIRMED = 'CONFIRMED', 'Confirmed by Hub'
        PICKUP_SCHEDULED = 'PICKUP_SCHEDULED', 'Pickup Scheduled'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    consumer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()
    contact_phone = models.CharField(max_length=15)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PLACED)
    payment_method = models.CharField(max_length=30, default='UPI_MOCK')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity_kg = models.DecimalField(max_digits=7, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    farmer_share = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2)

class DeliveryAssignment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_hub = models.CharField(max_length=150)
    drop_location = models.TextField()
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_completed_time = models.DateTimeField(null=True, blank=True)
    tracking_notes = models.TextField(blank=True, null=True)
```

### 15.5 `apps/market_intelligence/models.py`
```python
from django.db import models

class MarketBenchmarkPrice(models.Model):
    crop_name = models.CharField(max_length=100)
    mandi_name = models.CharField(max_length=120)
    district = models.CharField(max_length=100)
    modal_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    min_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    max_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    retail_estimated_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    recorded_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_date']

    def __str__(self):
        return f"{self.crop_name} @ {self.mandi_name} (₹{self.modal_price_per_kg}/kg)"
```

---

## 16. Django REST Framework (DRF) APIs & Endpoints

| Method | Endpoint | Description | Permitted Roles |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/token/` | Obtain JWT token | Public |
| `POST` | `/api/v1/auth/register/` | Register user (Farmer / Consumer / VDF) | Public |
| `GET` | `/api/v1/mandi/prices/` | List current mandi benchmark prices | All Authenticated |
| `POST` | `/api/v1/mandi/recommend-price/` | Calculate fair price range for given crop | Facilitator, Farmer |
| `GET` | `/api/v1/products/` | Public catalog with filters (radius, crop) | Public |
| `POST` | `/api/v1/products/create/` | Create produce listing | Facilitator, Farmer |
| `GET` | `/api/v1/products/<id>/breakdown/` | Get exact rupee price decomposition | Public |
| `POST` | `/api/v1/orders/create/` | Place direct consumer order | Consumer |
| `GET` | `/api/v1/orders/<id>/track/` | Real-time milestone status | Consumer, Delivery |
| `GET` | `/api/v1/analytics/kpis/` | Dashboard metrics for Admin & FPO | Admin |
| `GET` | `/api/v1/analytics/forecast/` | 7-day predicted crop demand | Admin, Facilitator |

---

## 17. Master URL Routing Blueprint

### Project-Level `agriconnect/urls.py`
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.marketplace.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    
    # App URLs
    path('accounts/', include('apps.accounts.urls')),
    path('facilitator/', include('apps.facilitators.urls')),
    path('farmer/', include('apps.farmers.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
    path('orders/', include('apps.orders.urls')),
    path('logistics/', include('apps.logistics.urls')),
    path('analytics/', include('apps.analytics.urls')),
    
    # API endpoints
    path('api/v1/', include([
        path('products/', include('apps.products.api_urls')),
        path('orders/', include('apps.orders.api_urls')),
        path('intelligence/', include('apps.market_intelligence.api_urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 18. Frontend & UI Component Blueprint

### 18.1 Master Base Layout (`templates/base.html`)
* Responsive Navbar with dynamic role badges (`[Farmer Mode]`, `[VDF Hub]`, `[Consumer Cart (3)]`).
* Toast notification container for flash alerts and mock SMS popups.
* Footer with direct language switcher (Hindi / English / Regional).

### 18.2 Key Interactive Views
1. **The Price Transparency Widget (`product_detail.html`):**
   * Visual progress bar decomposing the consumer rupee:
     * 🟢 **75% Farmer Realization** (Direct to bank/UPI)
     * 🟡 **5% Village Facilitator** (Quality check & packaging)
     * 🔵 **10% Cold Chain Logistics** (Shared tempo dispatch)
     * 🟣 **10% Platform & Insurance**
   * Direct comparison pill: *"Traditional Retail: ₹40/kg | You pay: ₹34/kg | Farmer gets: ₹28/kg"*.

2. **Village Facilitator Assisted Portal (`facilitator/add_listing.html`):**
   * Single-page fast entry optimized for low bandwidth.
   * **Voice Listing Button (Mic Icon):** Listens via Web Speech API (`webkitSpeechRecognition`). Automatically parses *"Tamatar 500 kilo bhav 25"* into Form fields.
   * **Fair Price Suggestion Alert:** Queries `/api/v1/mandi/recommend-price/` on crop select and alerts facilitator: *"Mandi rate is ₹22. Recommended fair listing: ₹26 - ₹30"*.

3. **Interactive IVR & Phone Simulator (`facilitator/ivr_voice_intake.html`):**
   * On-screen mobile phone keypad simulator.
   * Plays audio prompts / text readout:
     * Press 1: Daily Market Mandi Rates
     * Press 2: Sell Your Produce
     * Press 3: Check Payment Remittance Status
   * Allows hackathon judges to physically test how non-smartphone farmers interact with the platform.

4. **Leaflet.js Radius Map Search (`marketplace/catalog.html`):**
   * Interactive OpenStreetMap showing green markers for nearby farmer aggregation hubs.
   * Radius slider (5 km to 50 km) filtering catalog cards dynamically.

5. **Admin Analytics Dashboard (`analytics/admin_dashboard.html`):**
   * KPI stat cards (Registered Farmers, Total Revenue, Consumer Savings).
   * Chart.js integration showing price trends, crop demand curves, and order volume.

---

## 19. Machine Learning Engine Implementation

### 19.1 Demand Forecasting Model (`apps/analytics/ml_models/demand_predictor.py`)
```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

class CropDemandPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False

    def train_synthetic(self):
        """Train baseline model with agricultural seasonal patterns for demonstration."""
        np.random.seed(42)
        n_samples = 500
        
        # Features: [Month (1-12), APMC_Price, Season_Index (1: Rabi, 2: Kharif, 3: Zaid), Local_Stock_Kg]
        X = np.random.rand(n_samples, 4)
        X[:, 0] = np.random.randint(1, 13, n_samples)          # Month
        X[:, 1] = np.random.uniform(15, 60, n_samples)         # Benchmark Price
        X[:, 2] = np.random.randint(1, 4, n_samples)           # Season
        X[:, 3] = np.random.uniform(1000, 10000, n_samples)   # Supply

        # Target: Demand in kg for the upcoming week
        y = (X[:, 0] * 150) + (1000 - X[:, 1] * 8) + (X[:, 2] * 400) + np.random.normal(0, 50, n_samples)
        self.model.fit(X, y)
        self.is_trained = True

    def predict_next_week_demand(self, month, price, season, current_stock):
        if not self.is_trained:
            self.train_synthetic()
        features = np.array([[month, price, season, current_stock]])
        prediction = self.model.predict(features)[0]
        
        # Categorize output
        if prediction < 2000:
            level = "LOW"
        elif prediction < 4500:
            level = "MODERATE"
        elif prediction < 7000:
            level = "HIGH"
        else:
            level = "PEAK"
            
        return {
            'predicted_kg': round(prediction, 2),
            'demand_level': level
        }
```

---

## 20. Phased Development Order & Implementation Plan

```text
Phase 1: Environment & Authentication (Days 1–2)
├── Initialize Python virtual environment & Django project
├── Configure CustomUser model, roles, and migration scripts
├── Build base templates, static design system, and login/register views
└── Seed initial admin and test credentials

Phase 2: Assisted Portal & Farmer System (Days 3–4)
├── Build FarmerProfile and FacilitatorProfile models
├── Implement VDF dashboard and farmer registration views
├── Integrate Web Speech API for voice-assisted produce listing
└── Build interactive on-screen IVR Phone Simulator for jury demo

Phase 3: Catalog, Transparency & Geolocation (Days 5–6)
├── Create Category and Product models with price breakdown methods
├── Build Consumer Marketplace with Leaflet.js radius filtering
├── Implement Price Transparency Breakdown Card on product pages
└── Build MarketBenchmarkPrice model and daily price scraping/mock table

Phase 4: Cart, Orders & Dispatch (Days 7–8)
├── Implement session-based Shopping Cart and Checkout
├── Build Order, OrderItem, and DeliveryAssignment models
├── Create SMS Simulator (generating realistic notification alerts)
└── Build Delivery Partner Dispatch Sheet view

Phase 5: Analytics, ML & Polish (Days 9–10)
├── Implement Scikit-learn CropDemandPredictor
├── Build Admin Executive KPI Dashboard with Chart.js charts
├── Add supply-chain margin visualizer and savings metrics
└── Final end-to-end testing, responsive polish, and SIH presentation prep
```

---

## 21. SIH Pitching & Project Defense Strategy

* **Judge Inquiry:** *"Why would farmers trust a village facilitator instead of just going to their local mandi?"*
  * **Defense:** Farmers are already bound to village aggregators and commission agents who charge 8–12% cuts and delay payments by weeks. The VDF is an incentivized local resident whose transactions are recorded transparently with immediate digital payment confirmation and guaranteed fair benchmark rates.
* **Judge Inquiry:** *"How does this prevent middleman capture?"*
  * **Defense:** Disintermediation is audited by the **Price Transparency Breakdown** widget. Facilitator and platform fees are capped at fixed, publicly displayed percentages (5% each), making hidden markups mathematically impossible.
