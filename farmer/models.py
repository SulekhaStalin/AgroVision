
from django.db import models
from django.contrib.auth.models import User


class FarmerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    village = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    farm_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Crop(models.Model):

    CROP_STATUS = [
        ('Planted', 'Planted'),
        ('Growing', 'Growing'),
        ('Harvested', 'Harvested'),
    ]

    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name='crops'
    )

    crop_name = models.CharField(max_length=100)
    variety = models.CharField(max_length=100, blank=True)

    area = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    planting_date = models.DateField()
    expected_harvest_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=CROP_STATUS,
        default='Planted'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.crop_name


class Sale(models.Model):

    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name='sales'
    )

    crop = models.ForeignKey(
        Crop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_name = models.CharField(max_length=100)

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    unit = models.CharField(
        max_length=30,
        default='kg'
    )

    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    buyer_name = models.CharField(
        max_length=100,
        blank=True
    )

    sale_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_amount(self):
        return self.quantity * self.price_per_unit

    def __str__(self):
        return self.product_name
