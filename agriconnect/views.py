from django.shortcuts import render
from apps.marketplace.models import CustomerReview
from apps.products.models import Product, Category

def home_view(request):
    """
    Rich public landing page for AgriConnect (Krishi Setu).
    Passes live featured produce, categories, Mandi vs. AgriConnect price benchmarks,
    and rural impact indicators.
    """
    featured_products = Product.objects.filter(is_active=True).select_related('farmer__user', 'category')[:12]
    categories = Category.objects.all()

    mandi_comparisons = [
        {
            'name_en': 'Hybrid Tomatoes',
            'name_hi': 'हाइब्रिड टमाटर',
            'emoji': '🍅',
            'mandi_price': 42.0,
            'agri_price': 28.0,
            'savings_pct': 33,
            'farmer_gets': 21.0,
            'farmer_gets_pct': 75,
            'mandi_farmer_gets': 13.0,
            'village': 'Angara Hub, Ranchi',
        },
        {
            'name_en': 'Kufri Jyoti Potatoes',
            'name_hi': 'कुफरी ज्योति आलू',
            'emoji': '🥔',
            'mandi_price': 30.0,
            'agri_price': 22.5,
            'savings_pct': 25,
            'farmer_gets': 16.8,
            'farmer_gets_pct': 75,
            'mandi_farmer_gets': 9.5,
            'village': 'Getalsud Hub, Ranchi',
        },
        {
            'name_en': 'Nashik Red Onions',
            'name_hi': 'नासिक लाल प्याज',
            'emoji': '🧅',
            'mandi_price': 45.0,
            'agri_price': 35.0,
            'savings_pct': 22,
            'farmer_gets': 26.2,
            'farmer_gets_pct': 75,
            'mandi_farmer_gets': 15.0,
            'village': 'Garwa Village, Ranchi',
        },
        {
            'name_en': 'Spicy Green Chillies',
            'name_hi': 'तीखी हरी मिर्च',
            'emoji': '🌶️',
            'mandi_price': 95.0,
            'agri_price': 75.0,
            'savings_pct': 21,
            'farmer_gets': 56.2,
            'farmer_gets_pct': 75,
            'mandi_farmer_gets': 32.0,
            'village': 'Jonha Village, Ranchi',
        },
    ]

    impact_stats = {
        'kisans_onboarded': '1,280+',
        'village_hubs': '48',
        'direct_payouts_rupees': '₹42,80,000+',
        'avg_farm_to_fork_hours': '16.4 hrs',
        'food_miles_saved_pct': '68%',
    }

    # Load approved customer reviews for homepage
    live_reviews = CustomerReview.objects.filter(is_approved=True).order_by('-is_featured', '-submitted_at')[:6]

    context = {
        'featured_products': featured_products,
        'categories': categories,
        'mandi_comparisons': mandi_comparisons,
        'impact_stats': impact_stats,
        'live_reviews': live_reviews,
    }
    return render(request, 'public/home.html', context)
