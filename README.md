# AgriConnect 🌱
### Transparent Digital Agricultural Supply Chain Platform with Assisted-Digital Access

[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-Maps-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

---

## 📌 Overview

**AgriConnect** is an end-to-end digital agricultural supply chain platform engineered to disintermediate exploitative multi-tier middleman chains, provide real-time price transparency from official government Mandis, and bridge the digital literacy divide for rural farmers through an **assisted-digital ("phygital") access model**.

In conventional supply chains, farmers often receive only 20%–30% of the end-consumer retail value due to fragmented intermediaries (village brokers, commission agents, wholesalers, distributors, and retailers). AgriConnect connects farmers directly with retail consumers, institutional buyers, and bulk pools while providing complete visibility over freight, margins, and fair farmgate pricing.

---

## ✨ Key Features

### 1. 🧑‍🌾 Assisted-Digital Access (VDF Model & IVR)
* **Village Digital Facilitator (VDF) Portal:** Community agents onboard digitally excluded farmers, list produce on their behalf, coordinate transport, and disburse cash payouts.
* **Interactive Voice Response (IVR) & SMS Simulator:** Allows farmers with basic feature phones to check live mandi rates and list produce using automated phone prompts and SMS notifications.

### 2. 🛒 Transparent Direct-to-Consumer Marketplace
* **Fair Price Discovery:** Breakdown of consumer price vs. farmer realization vs. logistics cost on every listing.
* **Group Buying Pools:** Consumers in residential clusters or housing societies can aggregate bulk orders for volume discounts and optimized delivery batches.

### 3. 📊 Real-Time Mandi Market Intelligence
* **data.gov.in Integration:** Live Agmarknet market price data across commodities, mandis, and states.
* **Price Trend Visualizations:** Interactive Chart.js graphs displaying modal, minimum, and maximum prices to assist farmers in timing market sales.

### 4. 🚚 Integrated Logistics & Farmgate Pickup
* **Trip & Route Aggregation:** Transporters claim farmgate pickup requests and deliver consolidated batches.
* **Live Route Tracking:** Leaflet.js and OpenStreetMap route display with geofenced delivery verification.

### 5. 🛡️ Fair Escrow & Quality Dispute Resolution
* **Two-Party Verification:** Delivery OTP verification ensures both buyer and farmer/facilitator agree on goods receipt.
* **Resolution Workflow:** Built-in quality dispute filing with image evidence and platform mediator review.

---

## 🏗️ Architecture & Apps Structure

```text
AgriConnect/
├── agriconnect/              # Project settings, root routing, WSGI/ASGI
├── apps/
│   ├── accounts/             # Custom 5-role User model, auth & profile flows
│   ├── farmers/              # Farmer management, harvest logs, SMS/IVR simulator
│   ├── facilitators/         # Village Digital Facilitator (VDF) kiosk & operations
│   ├── products/             # Agricultural produce catalog, categories, units
│   ├── marketplace/          # Public browse, cart, search, group buying pools
│   ├── orders/               # Checkout, order states, dispute resolution
│   ├── logistics/            # Transporter dispatch, batching, Leaflet GPS tracking
│   ├── market_intelligence/  # data.gov.in Agmarknet Mandi API integration & charts
│   └── analytics/            # Margin breakdown & supply chain analytics
├── media/                    # Produce photos & sample product assets
├── static/                   # CSS, JavaScript (Leaflet, Chart.js, IVR simulator)
├── templates/                # Responsive HTML5 templates
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management CLI
└── test_full_suite.py        # Comprehensive test script
```

---

## 👥 Role-Based Access Control (RBAC)

AgriConnect supports 5 specialized user personas:

| Role | Default Dashboard | Capabilities |
| :--- | :--- | :--- |
| **Farmer** | `/farmer/dashboard/` | List crops, view earnings, monitor orders, access Mandi prices |
| **Facilitator (VDF)** | `/facilitator/dashboard/` | Register farmers, list crops for offline farmers, track deliveries |
| **Buyer / Consumer** | `/marketplace/` | Browse fresh produce, place orders, join bulk group buying pools |
| **Transporter** | `/logistics/dashboard/` | Accept farmgate pickup jobs, update GPS route checkpoints, verify delivery |
| **Admin / Mediator** | `/admin/` | Platform health monitoring, dispute mediation, user verification |

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.11 or higher
* Git

### 1. Clone the Repository
```bash
git clone https://github.com/aamir529/AgriConnect.git
cd AgriConnect
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional)* Add your free API key from [data.gov.in](https://data.gov.in) to enable live Agmarknet mandi feeds.

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Seed Demo Data (Optional for Quick Demo)
Populate sample users, crops, orders, and logistics data:
```bash
python manage.py seed_phase1
python manage.py seed_phase2
python manage.py seed_phase3
python manage.py seed_phase4
python manage.py seed_phase5
python manage.py seed_phase6
python manage.py seed_phase7
python manage.py seed_phase8
```

### 7. Launch Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your web browser.

---

## 🧪 Demo Credentials (After Seeding)

| Role | Username | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` |
| **Facilitator (VDF)** | `vdf_sunil` | `vdf123` |
| **Farmer** | `farmer_ramesh` | `farmer123` |
| **Consumer / Buyer** | `buyer_priya` | `buyer123` |
| **Transporter** | `transporter_vikram` | `transporter123` |

---

## 🧪 Automated Testing
Run the automated validation test suite:
```bash
python test_full_suite.py
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
