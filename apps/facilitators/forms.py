from django import forms
from django.utils import timezone
from apps.accounts.models import CustomUser
from apps.farmers.models import FarmerProfile
from apps.products.models import Product, Category

class FarmerOnboardingForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        label="Farmer's First Name (नाम)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ramesh'})
    )
    last_name = forms.CharField(
        max_length=50,
        label="Last Name (उपनाम)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Kumar / Mahto'})
    )
    phone = forms.CharField(
        max_length=15,
        label="Phone Number (फोन नंबर)",
        help_text="Will receive SMS updates about listings, orders, and payments",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9876543210'})
    )
    village = forms.CharField(
        max_length=100,
        label="Village / Tola (गाँव / टोला)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Jonha'})
    )
    land_area_acres = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=1.5,
        label="Land Area in Acres (जमीन - एकड़ में)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'})
    )
    primary_crops = forms.CharField(
        max_length=255,
        initial="Tomato, Potato, Cauliflower",
        label="Primary Crops Grown (मुख्य फसलें)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    bank_or_upi = forms.CharField(
        max_length=60,
        required=False,
        label="Bank Account / UPI ID (बैंक खाता या UPI)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9876543210@upi or SBI A/c'})
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("A farmer with this phone number is already registered.")
        return phone


class AssistedListingForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'farmer',
            'category',
            'name',
            'variety',
            'grade',
            'available_quantity_kg',
            'minimum_order_kg',
            'farmer_base_price_per_kg',
            'traditional_market_price_per_kg',
            'harvest_date',
            'emoji_icon',
            'image',
            'is_organic',
            'description',
        ]
        widgets = {
            'farmer': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_farmer'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'id': 'id_name', 'placeholder': 'e.g. Fresh Hybrid Tomatoes'}),
            'variety': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_variety', 'placeholder': 'e.g. Abhinav 1057'}),
            'grade': forms.Select(attrs={'class': 'form-select', 'id': 'id_grade'}),
            'available_quantity_kg': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'id': 'id_quantity', 'placeholder': 'e.g. 500'}),
            'minimum_order_kg': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_min_order', 'value': '5'}),
            'farmer_base_price_per_kg': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'id': 'id_farmer_price', 'placeholder': 'e.g. 25.00', 'step': '0.50'}),
            'traditional_market_price_per_kg': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_market_price', 'placeholder': 'e.g. 40.00', 'step': '0.50'}),
            'harvest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_harvest_date'}),
            'emoji_icon': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_emoji', 'value': '🍅'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'id_image', 'accept': 'image/*'}),
            'is_organic': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_organic'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'id': 'id_description'}),
        }

    def __init__(self, facilitator=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if facilitator:
            # Filter farmers to those assigned to this village facilitator
            self.fields['farmer'].queryset = FarmerProfile.objects.filter(facilitator=facilitator)
        if not self.initial.get('harvest_date'):
            self.initial['harvest_date'] = timezone.now().date()
