from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from .models import MarketBenchmarkPrice
from .services import MandiDataService

def mandi_prices_view(request):
    """
    Public live comparison view displaying daily APMC Mandi benchmark prices,
    traditional retail supermarket markups, and AgriConnect direct rates.
    Supports filtering by state, district, and crop search.
    """
    queryset = MarketBenchmarkPrice.objects.all()

    state_filter = request.GET.get('state', '').strip()
    district_filter = request.GET.get('district', '').strip()
    search_query = request.GET.get('q', '').strip()

    if state_filter:
        queryset = queryset.filter(state__iexact=state_filter)
    if district_filter:
        queryset = queryset.filter(district__iexact=district_filter)
    if search_query:
        queryset = queryset.filter(crop_name__icontains=search_query)

    # Get distinct states and districts for filters
    all_states = sorted(list(set(MarketBenchmarkPrice.objects.values_list('state', flat=True).distinct())))
    all_districts = sorted(list(set(MarketBenchmarkPrice.objects.values_list('district', flat=True).distinct())))

    # Augmented comparison calculations
    comparison_data = []
    for item in queryset:
        mandi = float(item.modal_price_per_kg)
        retail = float(item.retail_estimated_price_per_kg)
        
        # AgriConnect direct rate gives ~22% more to farmer while saving consumer ~20%
        agri_farmer = round(mandi * 1.22, 2)
        agri_consumer = round(agri_farmer * 1.25, 2) # with 5% VDF + 10% logistics + 10% platform
        
        farmer_gain_pct = round(((agri_farmer - mandi) / mandi) * 100, 1) if mandi > 0 else 0.0
        consumer_saving_pct = round(((retail - agri_consumer) / retail) * 100, 1) if retail > 0 else 0.0

        comparison_data.append({
            'item': item,
            'mandi_modal': mandi,
            'retail_price': retail,
            'agri_farmer_payout': agri_farmer,
            'agri_consumer_price': agri_consumer,
            'farmer_gain_pct': farmer_gain_pct,
            'consumer_saving_pct': consumer_saving_pct,
        })

    latest_item = MarketBenchmarkPrice.objects.order_by('-recorded_date').first()
    latest_date = latest_item.recorded_date if latest_item else None

    context = {
        'comparison_data': comparison_data,
        'states': all_states,
        'districts': all_districts,
        'selected_state': state_filter,
        'selected_district': district_filter,
        'search_query': search_query,
        'latest_date': latest_date,
        'is_custom_key': MandiDataService.is_custom_key_configured(),
        'total_benchmarks': queryset.count(),
    }
    return render(request, 'market_intelligence/mandi_prices.html', context)


def api_price_recommendation(request):
    """
    API endpoint returning fair price range recommendations for farmers & facilitators.
    """
    crop = request.GET.get('crop', '').strip()
    benchmark = None
    if crop:
        benchmark = MarketBenchmarkPrice.objects.filter(crop_name__icontains=crop).first()
    
    if benchmark:
        mandi = float(benchmark.modal_price_per_kg)
        retail = float(benchmark.retail_estimated_price_per_kg)
        rec_min = round(mandi * 1.15, 2)
        rec_max = round(retail * 0.78, 2)
    else:
        mandi = 22.00
        retail = 40.00
        rec_min = 25.00
        rec_max = 32.00

    return JsonResponse({
        'crop': crop or 'General Crop',
        'mandi_modal_price': mandi,
        'retail_benchmark_price': retail,
        'recommended_farmer_min': rec_min,
        'recommended_farmer_max': rec_max,
        'recommendation_text': f"Recommended listing: \u20b9{rec_min} to \u20b9{rec_max}/kg (Mandi rate is \u20b9{mandi}/kg).",
    })


@csrf_exempt
def api_sync_live_mandi(request):
    """
    AJAX endpoint allowing users to trigger live sync directly from the web interface.
    """
    state = request.GET.get('state') or request.POST.get('state')
    district = request.GET.get('district') or request.POST.get('district')

    res = MandiDataService.fetch_live_prices(state=state, district=district, limit=50)

    if res.get('success') and res.get('count', 0) > 0:
        return JsonResponse({
            'status': 'success',
            'source': res.get('source'),
            'count': res.get('count'),
            'message': f"Successfully synced {res['count']} live records directly from data.gov.in Agmarknet feed!",
            'is_rate_limited': False,
        })
    else:
        # Fallback refresh with today's date
        refreshed = MandiDataService.seed_latest_market_data()
        warn = res.get('error', 'API temporarily unavailable')
        return JsonResponse({
            'status': 'fallback',
            'count': refreshed,
            'warning': warn,
            'is_rate_limited': res.get('is_rate_limited', False),
            'message': f"Updated {refreshed} benchmark rates for today. Note: {warn}",
        })