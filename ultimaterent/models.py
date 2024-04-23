import datetime

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models
from django.forms import ModelForm, forms
from django.contrib.auth.models import User


class Property(models.Model):
    CATEGORY_CHOICES = [
        ('AP', 'Apartment'),
        ('VL', 'Villa'),
        ('HM', 'Home'),
        ('OF', 'Office'),
        # ... other categories ...
    ]
    SALE_OR_RENT_CHOICES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    ]
    GARAGE_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No')
    ]
    FURNISHING_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No')
    ]

    title = models.CharField(max_length=200)
    address = models.TextField()
    description = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True)  # Assuming phone number is optional
    email = models.EmailField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=50)  # 'rent' or 'sale'
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default='AP')

    # Corrected fields
    bhk = models.IntegerField(default=1)  # Assuming BHK is always a whole number
    area = models.DecimalField(max_digits=7, decimal_places=2, default=100.0)
    possession_date = models.DateField(null=True, blank=True)
    price_range = models.CharField(max_length=100, default='0৳ - 0৳')  # Display in dollars
    launch_date = models.DateField(null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Deposit Amount", null=True,
                                         blank=True)
    balconies = models.IntegerField(verbose_name="Balconies", null=True, blank=True)
    # furnishing_status = models.CharField(max_length=100, verbose_name="Furnishing", null=True, blank=True)
    furnishing_status = models.CharField(max_length=3, choices=FURNISHING_CHOICES, default='NO')
    bedroom_count = models.IntegerField(verbose_name="Bedrooms", null=True, blank=True)
    bathroom_count = models.IntegerField(verbose_name="Baths", null=True, blank=True)
    garage = models.CharField(max_length=3, choices=GARAGE_CHOICES, default='NO')
    sale_or_rent = models.CharField(max_length=4, choices=SALE_OR_RENT_CHOICES, default='sale',
                                    verbose_name="Property For")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def _str_(self):
        return self.title


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='')
    agent_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=254, unique=True, default='')  # Provide a default value
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    application_date = models.DateTimeField(default=datetime.datetime.now)

    # Add other fields relevant to your agent model, such as name, contact info, etc.

    def __str__(self):
        return self.agent_id


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_appointments')
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Appointment with {self.agent.username} on {self.date} at {self.time}"


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyForm(ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'address', 'description', 'price', 'type', 'category', 'bhk', 'possession_date', 'area',
                  'price_range', 'launch_date']

    def clean_title(self):
        title = self.cleaned_data['title']
        # Add your custom validation code for title here.
        # For example, checking if the title is too long:
        if len(title) > 100:
            raise forms.ValidationError("Title is too long.")
        return title


class VisitSchedule(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    property = models.ForeignKey(Property, related_name='visit_schedules', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    preferred_date = models.DateField()
    additional_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.name} - {self.preferred_date.strftime('%Y-%m-%d')} ({self.status})"


class Offer(models.Model):
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='offers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_offers')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s offer on {self.property.title} for {self.amount}"
