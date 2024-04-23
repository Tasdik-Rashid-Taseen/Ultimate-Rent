from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.forms import ModelForm, forms, modelformset_factory

from .backends import User
from .models import Property, Agent  # Ensure this import is correct
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django import forms
from django.forms import ModelForm
from .models import PropertyImage
from .models import VisitSchedule


class PropertyForm(ModelForm):
    launch_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    possession_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'phone-number', 'placeholder': 'Phone Number'}),
        required=False  # Set to True if the phone number is required
    )

    class Meta:
        model = Property
        fields = ['title', 'address', 'description', 'phone_number', 'email', 'price', 'sale_or_rent', 'type',
                  'category',
                  'bhk', 'possession_date', 'area', 'price_range', 'launch_date',
                  'deposit_amount', 'balconies', 'furnishing_status', 'bedroom_count',
                  'bathroom_count', 'garage']

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise forms.ValidationError("Title is too long.")
        return title

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        # Additional custom validations can go here
        return email


class PropertyImageForm(ModelForm):
    image = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = PropertyImage
        fields = ['image']

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')

        if image:
            # Adjust the size limit as per your requirements
            if image.size > 2 * 1024 * 1024:  # 1 MB (example limit)
                self.add_error('image', forms.ValidationError(
                    f"Image file '{image.name}' is too large ( > 1MB )"))
        return cleaned_data


PropertyImageFormSet = modelformset_factory(
    PropertyImage,
    form=PropertyImageForm,
    extra=1,
    max_num=10,
)


class VisitScheduleForm(forms.ModelForm):
    class Meta:
        model = VisitSchedule
        fields = ['name', 'email', 'preferred_date', 'additional_notes']


class AgentSignupForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User", empty_label="Choose a user")
    name = forms.CharField(max_length=100, required=True)
    agent_id = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput, required=True)

    class Meta:
        model = Agent
        fields = ['user', 'name', 'agent_id', 'email', 'phone_number']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_agent_id(self):
        agent_id = self.cleaned_data.get('agent_id')
        if Agent.objects.filter(agent_id=agent_id).exists():
            raise forms.ValidationError("This agent ID is already in use.")
        return agent_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Agent.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use by another agent.")
        return email

    def save(self, commit=True):
        agent = super().save(commit=False)
        username = self.cleaned_data.get('username')  # Use .get to avoid KeyError
        if not username:
            # Handle the case where 'username' is not provided
            username = 'default_username'  # Set a default or derive from another field

        user = User.objects.create_user(
            username=username,
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        if commit:
            agent.user = user
            agent.save()
        return agent


class AppointmentForm(forms.Form):
    # Add your appointment form fields here
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'text', 'class': 'datepicker'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
