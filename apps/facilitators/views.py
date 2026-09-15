from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import json

from apps.accounts.decorators import role_required
from apps.accounts.models import CustomUser
from apps.farmers.models import FarmerProfile, FarmerSMSLog
from apps.products.models import Product, Category
from .models import FacilitatorProfile
from .forms import FarmerOnboardingForm, AssistedListingForm

def get_or_create_facilitator_profile(user):
    """Helper to ensure FacilitatorProfile exists for user."""
    profile, created = FacilitatorProfile.objects.get_or_create(
        user=user,
        defaults={
            'village_name': user.village_or_city or "Angara Village",
            'center_name': f"{user.village_or_city or 'Village'} Digital CSC Hub",
            'assigned_district': user.district or "Ranchi",
            'commission_percentage': Decimal('5.00')
        }
    )
    return profile


@role_required(['FACILITATOR', 'ADMIN'])
def facilitator_dashboard_view(request):
    profile = get_or_create_facilitator_profile(request.user)
    village_farmers = profile.farmers.all().select_related('user')
    listings = Product.objects.filter(farmer__facilitator=profile).select_related('farmer__user', 'category').order_by('-created_at')

    # Calculate summary metrics
    total_volume_kg = sum([p.available_quantity_kg for p in listings])
    total_estimated_value = sum([p.available_quantity_kg * p.farmer_base_price_per_kg for p in listings])
    hub_commission_estimate = round(float(total_estimated_value) * 0.05, 2)

    context = {
        'profile': profile,
        'farmers': village_farmers,
        'listings': listings,
        'total_volume_kg': total_volume_kg,
        'total_estimated_value': total_estimated_value,
        'hub_commission_estimate': hub_commission_estimate,
    }
    return render(request, 'facilitator/dashboard.html', context)


@role_required(['FACILITATOR', 'ADMIN'])
def register_farmer_view(request):
    profile = get_or_create_facilitator_profile(request.user)

    if request.method == 'POST':
        form = FarmerOnboardingForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            village = form.cleaned_data['village']
            land_acres = form.cleaned_data['land_area_acres']
            crops = form.cleaned_data['primary_crops']
            bank_upi = form.cleaned_data['bank_or_upi']

            # Create User Account for the Farmer
            username = f"farmer_{phone[-6:]}"
            user = CustomUser.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=CustomUser.Role.FARMER,
                village_or_city=village,
                district=profile.assigned_district,
                preferred_language='Hindi',
                is_verified=True
            )
            user.set_password('farmer123')
            user.save()

            # Create FarmerProfile linked to this Facilitator
            farmer_profile = FarmerProfile.objects.create(
                user=user,
                facilitator=profile,
                land_area_acres=land_acres,
                primary_crops=crops,
                upi_id=bank_upi if '@' in bank_upi else None,
                bank_account_number=bank_upi if '@' not in bank_upi else None,
                is_assisted_only=True
            )

            # Send Simulated SMS Confirmation
            FarmerSMSLog.objects.create(
                farmer=farmer_profile,
                alert_type=FarmerSMSLog.AlertType.MARKET_ALERT,
                phone_number=phone,
                message_text=f"Namaste {first_name} ji! Aapka panjikaran {profile.village_name} digital hub me ho gaya hai. VDF: {profile.user.get_full_name()}."
            )

            messages.success(
                request,
                f"Farmer {first_name} {last_name} successfully registered under {profile.village_name} Hub!"
            )
            return redirect('facilitator_dashboard')
    else:
        form = FarmerOnboardingForm(initial={'village': profile.village_name})

    return render(request, 'facilitator/register_farmer.html', {'form': form, 'profile': profile})


@role_required(['FACILITATOR', 'ADMIN'])
def add_listing_view(request):
    profile = get_or_create_facilitator_profile(request.user)

    if request.method == 'POST':
        form = AssistedListingForm(facilitator=profile, data=request.POST, files=request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Record Simulated SMS alert to the Farmer
            FarmerSMSLog.objects.create(
                farmer=product.farmer,
                alert_type=FarmerSMSLog.AlertType.LISTING_CREATED,
                phone_number=product.farmer.user.phone,
                message_text=(
                    f"Aapki {product.available_quantity_kg} kg {product.name} ki soochi ₹{product.farmer_base_price_per_kg}/kg "
                    f"ke bhav se AgriConnect par darj ho gayi hai. Hub: {profile.village_name}."
                )
            )

            messages.success(
                request,
                f"Batch '{product.name}' ({product.available_quantity_kg} kg) listed successfully for {product.farmer.user.get_full_name()}!"
            )
            return redirect('facilitator_dashboard')
    else:
        initial_farmer_id = request.GET.get('farmer_id')
        initial_data = {}
        if initial_farmer_id:
            initial_data['farmer'] = initial_farmer_id
        form = AssistedListingForm(facilitator=profile, initial=initial_data)

    categories = Category.objects.all()
    context = {
        'form': form,
        'profile': profile,
        'categories': categories,
    }
    return render(request, 'facilitator/add_listing.html', context)


def ivr_simulator_view(request):
    """
    On-screen smartphone dialer simulation for SIH Evaluators.
    Demonstrates how a farmer with a basic keypad phone accesses the platform.
    """
    return render(request, 'facilitator/ivr_simulator.html')


@csrf_exempt
def ivr_api_action(request):
    """
    Endpoint responding to simulated DTMF key presses and voice intake from the IVR dialer.
    """
    if request.method == 'POST':
        action = None
        key = ''
        try:
            data = json.loads(request.body)
            action = data.get('action')
            key = str(data.get('key') or data.get('digit', '')).strip()
            crop_name = data.get('crop_name', 'टमाटर (Tomato)')
            quantity_kg = data.get('quantity_kg', 500)
        except Exception:
            action = request.POST.get('action')
            key = request.POST.get('key') or request.POST.get('digit', '')
            crop_name = request.POST.get('crop_name', 'टमाटर (Tomato)')
            quantity_kg = request.POST.get('quantity_kg', 500)

        # Handle Simulated Voice Harvest Intake (Option 2 speech submit)
        if action == 'register_harvest' or key == 'submit_harvest':
            # Create simulated SMS log for farmer
            farmer = FarmerProfile.objects.first()
            sms_text = (
                f"IVR Alert: Aapka {quantity_kg} kg {crop_name} bikri hetu darj ho gaya hai. "
                f"VDF Sunil Mahto verification ke liye jald sampark karenge. Krishi Setu 1800-890-KISAN."
            )
            if farmer:
                FarmerSMSLog.objects.create(
                    farmer=farmer,
                    alert_type=FarmerSMSLog.AlertType.LISTING_CREATED,
                    phone_number=farmer.user.phone or "+919876543210",
                    message_text=sms_text
                )

            return JsonResponse({
                'title': 'फसल पंजीकरण सफल (Produce Registered)',
                'speech': f'धन्यवाद! आपका {quantity_kg} किलो {crop_name} का अनुरोध सफलतापूर्वक दर्ज कर लिया गया है। आपके ग्राम मित्र सुनील महतो को सूचना भेज दी गई है। आपके मोबाइल पर पुष्टि का एसएमएस भेजा गया है।',
                'speech_hinglish': f'Dhanyawad! Aapka {quantity_kg} kilo {crop_name} ka anurodh darj kar liya gaya hai. Gram Mitra Sunil Mahto ko soochana bhej di gayi hai. SMS bheja gaya hai.',
                'speech_en': f'Thank you! Your request to sell {quantity_kg} kilograms of produce has been registered. Village facilitator Sunil Mahto has been notified. Confirmation SMS sent.',
                'display': f'✓ सफलतापूर्वक दर्ज: {quantity_kg} kg {crop_name}\nएसएमएस भेजा गया | ग्राम मित्र सुनील महतो सूचित।',
                'sms_text': sms_text,
                'next_prompt': 'मुख्य मेन्यू के लिए स्टार दबाएं।'
            })

        # Responses for simulated 1800-890-KISAN call menu
        menu_responses = {
            '1': {
                'title': 'दैनिक मंडी भाव (Daily Mandi Rates)',
                'speech': 'आज रांची मुख्य मंडी में टमाटर 24 रुपये, आलू 18 रुपये, और प्याज 28 रुपये प्रति किलो है। एग्रीकनेक्ट पर किसानों को 4 से 6 रुपये अधिक मिल रहे हैं।',
                'speech_hinglish': 'Aaj Ranchi mandi me tamatar 24 rupaye, aalu 18 rupaye, aur pyaz 28 rupaye prati kilo hai. AgriConnect par kisano ko 4 se 6 rupaye adhik mil rahe hain. Fasal bechne ke liye 2 dabayein, ya sahayak se baat karne ke liye 4 dabayein.',
                'speech_en': 'Today in Ranchi Main Mandi, Tomato is 24 rupees, Potato is 18 rupees, and Onion is 28 rupees per kilogram. On AgriConnect, farmers receive 4 to 6 rupees more per kg. Press 2 to sell produce, or 4 to talk to facilitator.',
                'display': [
                    {'crop': 'Tomato (टमाटर)', 'mandi_rate': '₹24 / kg', 'agriconnect_rate': '₹28 / kg', 'benefit': '+16%'},
                    {'crop': 'Potato (आलू)', 'mandi_rate': '₹18 / kg', 'agriconnect_rate': '₹22 / kg', 'benefit': '+22%'},
                    {'crop': 'Onion (प्याज)', 'mandi_rate': '₹28 / kg', 'agriconnect_rate': '₹34 / kg', 'benefit': '+21%'},
                ],
                'next_prompt': 'फसल बेचने के लिए 2 दबाएं, या प्रतिनिधि से बात करने के लिए 4 दबाएं।'
            },
            '2': {
                'title': 'फसल बिक्री पंजीकरण (Register Produce)',
                'speech': 'अपनी फसल बेचने के लिए बीप के बाद फसल का नाम और मात्रा बोलें। उदाहरण: 500 किलो टमाटर। आपका ग्राम मित्र सुनील महतो इसे सत्यापित करेगा।',
                'speech_hinglish': 'Apni fasal bechne ke liye beep ke baad fasal ka naam aur matra bolein. Jaise 500 kilo tamatar. Aapka gram mitra Sunil Mahto ise verify karega.',
                'speech_en': 'To sell your produce, speak the crop name and quantity after the beep. For example: 500 kilograms of tomatoes. Your village facilitator Sunil Mahto will verify it.',
                'display': 'वॉइस इनपुट सक्रिय: बीप के बाद बोलें "मेरे पास 500 किलो टमाटर है..."',
                'action_required': 'voice_input',
                'next_prompt': 'मुख्य मेन्यू के लिए स्टार दबाएं।'
            },
            '3': {
                'title': 'भुगतान व ऑर्डर स्थिति (Payment & Order Status)',
                'speech': 'रमेश कुमार जी, आपके पिछले 400 किलो टमाटर का 11,200 रुपये का भुगतान आपके बैंक खाते में जमा कर दिया गया है। नया ऑर्डर जांचने के लिए 0 दबाएं।',
                'speech_hinglish': 'Ramesh Kumar ji, aapke pichle 400 kilo tamatar ka 11,200 rupaye ka payment aapke bank account me jama kar diya gaya hai. Naya order ke liye 0 dabayein.',
                'speech_en': 'Ramesh Kumar ji, payment of 11,200 rupees for your previous 400 kilograms of tomatoes has been credited to your bank account. Press 0 to check new orders. Press star for main menu.',
                'display': 'पिछला भुगतान: ₹11,200 (SBI A/c •••• 4021) - सफल। SMS भेजा गया।',
                'next_prompt': 'नया ऑर्डर जांचने के लिए 0 दबाएं, या मुख्य मेन्यू के लिए स्टार दबाएं।'
            },
            '4': {
                'title': 'ग्राम डिजिटल मित्र से संपर्क (Connect with Facilitator)',
                'speech': 'आपकी कॉल आपके निकटतम ग्राम मित्र सुनील महतो (अंगड़ा केंद्र) से जोड़ी जा रही है। कृपया प्रतीक्षा करें...',
                'speech_hinglish': 'Aapki call aapke nikat-tam gram mitra Sunil Mahto, Angara hub se jodi ja rahi hai. Kripya wait karein.',
                'speech_en': 'Connecting your call to your nearest village facilitator Sunil Mahto, Angara Village Hub. Please hold...',
                'display': 'Connecting to VDF Sunil Mahto: +91 9800000002 (Angara Village Hub)',
                'next_prompt': 'कॉल समाप्त करने के लिए लाल बटन दबाएं।'
            },
            '*': {
                'title': 'मुख्य मेन्यू (Main Menu)',
                'speech': 'मुख्य मेन्यू: दैनिक मंडी भाव के लिए 1 दबाएं। अपनी फसल बेचने के लिए 2 दबाएं। भुगतान और ऑर्डर स्थिति के लिए 3 दबाएं। ग्राम मित्र से संपर्क के लिए 4 दबाएं।',
                'speech_hinglish': 'Main Menu: Mandi bhav ke liye 1 dabayein. Fasal bechne ke liye 2 dabayein. Payment ke liye 3 dabayein. Gram Mitra ke liye 4 dabayein.',
                'speech_en': 'Main Menu: Press 1 for Mandi Rates. Press 2 to sell harvest. Press 3 for payment status. Press 4 for village facilitator.',
                'display': "1: मंडी भाव | 2: फसल बेचें\n3: भुगतान स्थिति | 4: ग्राम मित्र",
                'next_prompt': '1, 2, 3 या 4 में से कोई बटन दबाएं।'
            },
            '0': {
                'title': 'नया मांग ऑर्डर (New Market Demand)',
                'speech': 'आज रांची बाजार से 500 किलो टमाटर और 200 किलो शिमला मिर्च की तत्काल सामूहिक मांग उपलब्ध है। अपनी फसल बुक करने के लिए 2 दबाएं।',
                'speech_hinglish': 'Aaj Ranchi market se 500 kilo tamatar aur 200 kilo shimla mirch ki urgent demand uplabdh hai. Fasal book karne ke liye 2 dabayein.',
                'speech_en': 'Today there is active market demand for 500 kg Tomatoes and 200 kg Capsicum in Ranchi. Press 2 to book your harvest.',
                'display': "सक्रिय मांग:\n• टमाटर: 500 kg @ ₹28/kg (+16% Mandi)\n• शिमला मिर्च: 200 kg @ ₹42/kg (+20%)",
                'next_prompt': 'फसल बुक करने के लिए 2 दबाएं, मुख्य मेन्यू के लिए * दबाएं।'
            },
            '#': {
                'title': 'किसान सहायता (Kisan Helpline Support)',
                'speech': 'यह एग्रीकनेक्ट किसान आईवीआर हेल्पलाइन 1800-890-KISAN है। मंडी भाव के लिए 1, फसल बेचने के लिए 2, भुगतान के लिए 3, ग्राम मित्र के लिए 4 दबाएं।',
                'speech_hinglish': 'Yeh AgriConnect Kisan Helpline 1800-890-KISAN hai. Mandi bhav ke liye 1, fasal bechne ke liye 2, payment ke liye 3, gram mitra ke liye 4 dabayein.',
                'speech_en': 'This is AgriConnect Kisan Helpline 1800-890-KISAN. Press 1 for Mandi rates, 2 to sell, 3 for payout status, 4 for village facilitator.',
                'display': "टोल-फ्री हेल्पलाइन: 1800-890-KISAN\nसमय: प्रातः 6 बजे से सायं 8 बजे तक (प्रतिदिन)",
                'next_prompt': 'मेन्यू विकल्प चुनने के लिए बटन दबाएं।'
            }
        }

        response_data = menu_responses.get(
            key,
            {
                'title': 'अमान्य विकल्प (Invalid Option)',
                'speech': 'अमान्य बटन दबाया गया है। मंडी भाव के लिए 1, फसल बेचने के लिए 2, भुगतान के लिए 3, ग्राम मित्र के लिए 4 दबाएं।',
                'speech_hinglish': 'Galat button dabaya gaya hai. Mandi rate ke liye 1, fasal bechne ke liye 2, payment ke liye 3, gram mitra ke liye 4 dabayein.',
                'speech_en': 'Invalid button pressed. Press 1 for Mandi rates, 2 to sell produce, 3 for payment status, 4 for village facilitator.',
                'display': 'कृपया 1, 2, 3 या 4 में से कोई बटन दबाएं।',
                'next_prompt': 'मेन्यू दोहराया जा रहा है।'
            }
        )
        return JsonResponse(response_data)

    return JsonResponse({'error': 'POST method required'}, status=400)

