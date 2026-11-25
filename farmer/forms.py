
from django import forms
from django.contrib.auth.models import User
from .models import FarmerProfile
from .models import FarmerProfile, Crop, Sale

class FarmerRegistrationForm(forms.ModelForm):

    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta:
        model = FarmerProfile
        fields = [
            'full_name',
            'phone',
            'address',
            'village',
            'district',
            'state',
            'farm_size'
        ]

    def save(self, commit=True):
        farmer = super().save(commit=False)

        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )

        farmer.user = user

        if commit:
            farmer.save()

        return farmer

from .models import Crop

class CropForm(forms.ModelForm):

    class Meta:
        model = Crop
        fields = [
            'crop_name',
            'variety',
            'area',
            'planting_date',
            'expected_harvest_date',
            'status'
        ]

        widgets = {
            'planting_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'expected_harvest_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }

class FarmerProfileForm(forms.ModelForm):

    class Meta:
        model = FarmerProfile
        fields = [
            'full_name',
            'phone',
            'address',
            'village',
            'district',
            'state',
            'farm_size'
        ]

        widgets = {
            'address': forms.Textarea(
                attrs={'rows': 3}
            ),
        }

class SaleForm(forms.ModelForm):

    class Meta:
        model = Sale
        fields = [
            'crop',
            'product_name',
            'quantity',
            'unit',
            'price_per_unit',
            'buyer_name',
            'sale_date'
        ]

        widgets = {
            'sale_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }

    def __init__(self, *args, farmer=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['crop'].required = False

        if farmer:
            self.fields['crop'].queryset = Crop.objects.filter(
                farmer=farmer
            )
