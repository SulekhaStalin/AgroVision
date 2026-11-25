
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth

from .forms import (
    FarmerRegistrationForm,
    CropForm,
    FarmerProfileForm,
    SaleForm
)

from .models import FarmerProfile, Crop


# FARMER REGISTRATION
def register_farmer(request):

    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)

        if form.is_valid():
            farmer = form.save()
            login(request, farmer.user)

            messages.success(
                request,
                'Registration successful! Welcome to AgroVision.'
            )

            return redirect('farmer_dashboard')

    else:
        form = FarmerRegistrationForm()

    return render(
        request,
        'farmer/register.html',
        {'form': form}
    )


# FARMER LOGIN
def farmer_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if FarmerProfile.objects.filter(user=user).exists():

                login(request, user)

                messages.success(
                    request,
                    'Login successful!'
                )

                return redirect('farmer_dashboard')

        messages.error(
            request,
            'Invalid farmer credentials.'
        )

    return render(
        request,
        'farmer/login.html'
    )


# FARMER LOGOUT
def farmer_logout(request):

    logout(request)

    return redirect('home')


# FARMER DASHBOARD
@login_required
def farmer_dashboard(request):

    farmer = get_object_or_404(
        FarmerProfile,
        user=request.user
    )

    # Farmer crops and sales
    crops = farmer.crops.all().order_by('-created_at')
    sales = farmer.sales.all().order_by('-sale_date')

    # BASIC ANALYTICS
    total_crops = crops.count()
    total_sales = sales.count()

    total_revenue = sum(
        sale.total_amount for sale in sales
    )

    # MONTHLY REVENUE ANALYTICS
    monthly_sales = (
        sales.annotate(
            month=TruncMonth('sale_date')
        )
        .values('month')
        .annotate(
            revenue=Sum(
                ExpressionWrapper(
                    F('quantity') * F('price_per_unit'),
                    output_field=DecimalField(
                        max_digits=20,
                        decimal_places=2
                    )
                )
            )
        )
        .order_by('month')
    )

    chart_labels = [
        item['month'].strftime('%b %Y')
        for item in monthly_sales
    ]

    chart_values = [
        float(item['revenue'])
        for item in monthly_sales
    ]

    # HARVEST REMINDERS
    today = timezone.localdate()

    next_30_days = today + timedelta(days=30)

    upcoming_harvests = crops.filter(
        expected_harvest_date__gte=today,
        expected_harvest_date__lte=next_30_days
    ).exclude(
        status='Harvested'
    ).order_by(
        'expected_harvest_date'
    )

    # DASHBOARD CONTEXT
    context = {
        'farmer': farmer,
        'crops': crops,
        'sales': sales,

        'total_crops': total_crops,
        'total_sales': total_sales,
        'total_revenue': total_revenue,

        'chart_labels': chart_labels,
        'chart_values': chart_values,

        'upcoming_harvests': upcoming_harvests,
    }

    return render(
        request,
        'farmer/dashboard.html',
        context
    )


# ADD CROP
@login_required
def add_crop(request):

    farmer = get_object_or_404(
        FarmerProfile,
        user=request.user
    )

    if request.method == 'POST':

        form = CropForm(request.POST)

        if form.is_valid():

            crop = form.save(commit=False)
            crop.farmer = farmer
            crop.save()

            messages.success(
                request,
                'Crop added successfully!'
            )

            return redirect('farmer_dashboard')

    else:
        form = CropForm()

    return render(
        request,
        'farmer/add_crop.html',
        {'form': form}
    )


# EDIT CROP
@login_required
def edit_crop(request, crop_id):

    farmer = get_object_or_404(
        FarmerProfile,
        user=request.user
    )

    crop = get_object_or_404(
        Crop,
        id=crop_id,
        farmer=farmer
    )

    if request.method == 'POST':

        form = CropForm(
            request.POST,
            instance=crop
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Crop updated successfully!'
            )

            return redirect('farmer_dashboard')

    else:
        form = CropForm(instance=crop)

    return render(
        request,
        'farmer/edit_crop.html',
        {
            'form': form,
            'crop': crop
        }
    )


# DELETE CROP
@login_required
def delete_crop(request, crop_id):

    farmer = get_object_or_404(
        FarmerProfile,
        user=request.user
    )

    crop = get_object_or_404(
        Crop,
        id=crop_id,
        farmer=farmer
    )

    if request.method == 'POST':

        crop.delete()

        messages.success(
            request,
            'Crop deleted successfully!'
        )

        return redirect('farmer_dashboard')

    return render(
        request,
        'farmer/delete_crop.html',
        {'crop': crop}
    )


# EDIT FARMER PROFILE
@login_required
def edit_profile(request):

    farmer = get_object_or_404(
        FarmerProfile,
        user=request.user
    )

    if request.method == 'POST':

        form = FarmerProfileForm(
            request.POST,
            instance=farmer
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Profile updated successfully!'
            )

            return redirect('farmer_dashboard')

    else:
        form = FarmerProfileForm(
            instance=farmer
        )

    return render(
        request,
        'farmer/edit_profile.html',
        {
            'form': form,
            'farmer': farmer
        }
    )


# ADD SALE
@login_required
def add_sale(request):

    farmer = get_object_or_404(
        FarmerProfile,
        user=request.user
    )

    if request.method == 'POST':

        form = SaleForm(
            request.POST,
            farmer=farmer
        )

        if form.is_valid():

            sale = form.save(commit=False)
            sale.farmer = farmer
            sale.save()

            messages.success(
                request,
                'Sale recorded successfully!'
            )

            return redirect('farmer_dashboard')

    else:
        form = SaleForm(
            farmer=farmer
        )

    return render(
        request,
        'farmer/add_sale.html',
        {'form': form}
    )
