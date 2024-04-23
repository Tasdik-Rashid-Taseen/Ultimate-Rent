from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes
from ultrent import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.core.mail import EmailMessage, send_mail
from .tokens import generate_token
from .forms import PropertyForm, PropertyImageForm, PropertyImageFormSet, VisitScheduleForm, AppointmentForm, \
    AgentSignupForm
from .models import Property, PropertyImage, VisitSchedule, Offer, Agent, Appointment
from django.db.models import Q
import stripe

User = get_user_model()


def home(request):
    properties = Property.objects.all()[:10]  # Example: Limit to the first 10 properties

    categories = Property.CATEGORY_CHOICES
    sale_or_rent_choices = list(Property.SALE_OR_RENT_CHOICES)
    for i, (code, name) in enumerate(sale_or_rent_choices):
        if code == 'sale':
            sale_or_rent_choices[i] = (code, 'Buy')

    addresses = Property.objects.exclude(address__isnull=True).order_by('address').values_list('address',
                                                                                               flat=True).distinct()
    bedroom_counts = (Property.objects.exclude(bedroom_count__isnull=True).exclude
                      (bedroom_count__lte=-1).order_by('bedroom_count').values_list('bedroom_count',
                                                                                   flat=True).distinct())

    bathroom_counts = (Property.objects.exclude(bathroom_count__isnull=True).exclude
                      (bathroom_count__lte=-1).order_by('bathroom_count').values_list('bathroom_count',
                                                                          flat=True).distinct())
    garages = (Property.objects.exclude(garage__isnull=True).exclude
                      (garage__lte=-1).order_by('garage').values_list('garage',
                                                                          flat=True).distinct())
    balconies_s = (Property.objects.exclude(balconies__isnull=True).exclude
                      (balconies__lte=-1).order_by('balconies').values_list('balconies',
                                                                          flat=True).distinct())

    # Pass the additional context to the template
    context = {
        'properties': properties,
        'categories': categories,
        'sale_or_rent_choices': sale_or_rent_choices,
        'addresses': addresses,
        'bedroom_counts': bedroom_counts,
        'bathroom_counts': bathroom_counts,
        'garages': garages,
        'balconies_s': balconies_s,
    }
    return render(request, 'index.html', context)


def search(request):
    # Start with a base query
    query = Property.objects.all()

    # Get parameters from the request
    keyword = request.GET.get('keyword', '')
    category = request.GET.get('category', '')
    sale_or_rent = request.GET.get('sale_or_rent', '')
    address = request.GET.get('address', '')
    bedroom_count = request.GET.get('bedroom_count', '')
    bathroom_count = request.GET.get('bathroom_count', '')
    garage = request.GET.get('garage', '')
    balconies = request.GET.get('balconies', '')

    # Apply filters if parameters are provided
    if keyword:
        query = query.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
    if category:
        query = query.filter(category=category)
    if sale_or_rent:
        query = query.filter(sale_or_rent=sale_or_rent)
    if address:
        query = query.filter(address__icontains=address)
    if bedroom_count:
        query = query.filter(bedroom_count=bedroom_count)
    if bathroom_count:
        query = query.filter(bathroom_count=bathroom_count)
    if garage:
        query = query.filter(garage=garage.upper())
    if balconies:
        query = query.filter(balconies=balconies)

    # Extract unique values for filters dynamically from the filtered query
    unique_bedroom = set(property.bedroom_count for property in query if property.bedroom_count)
    unique_bathroom = set(property.bathroom_count for property in query if property.bathroom_count)
    unique_garage = set(property.garage for property in query if property.garage)
    unique_balconies = set(property.balconies for property in query if property.balconies)

    context = {
        'properties': query,
        'unique_balconies': unique_balconies,
        'unique_bedroom': unique_bedroom,
        'unique_bathroom': unique_bathroom,
        'unique_garage': unique_garage
    }

    return render(request, 'search_results.html', context)

@login_required
def add_property_view(request):
    PropertyImageFormSet = modelformset_factory(PropertyImage, form=PropertyImageForm, extra=1)
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        formset = PropertyImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            property_instance = form.save(commit=False)  # Create a property instance without saving
            property_instance.user = request.user  # Set the user field
            property_instance.save()  # Save the property instance with the user set
            # Handle multiple image files
            images = request.FILES.getlist('form-0-image')  # 'form-0-image' is the name of the file input
            for image in images:
                PropertyImage.objects.create(property=property_instance, image=image)
            return redirect('home')
    else:
        form = PropertyForm()
        formset = PropertyImageFormSet(queryset=PropertyImage.objects.none())
    return render(request, 'add_property.html', {'form': form, 'formset': formset})


def signup(request):
    if request.method == "POST":
        # Get data from form
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # Various validations
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('signup')
        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters")
            return redirect('signup')
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match")
            return redirect('signup')
        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric")
            return redirect('signup')

        # Create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False  # User will be activated after email confirmation
        myuser.save()

        # Confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirm your email @ Ultimate Rent"
        message = render_to_string('email_confirmation.html', {
            'user': myuser,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        messages.success(request,
                         "Your account has been successfully created. Please confirm your email address to activate your account.")
        return redirect('signup')

    return render(request, "signup.html")


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect('signin')
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect('signup')


def signin(request):
    # Capture the 'next' parameter from the query string for GET requests or default to '/'
    next_url = request.GET.get('next', '/')

    if request.method == "POST":
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')

        # For POST requests, 'next' might be part of the form data
        next_url = request.POST.get('next', next_url)

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            return redirect(next_url)  # Redirect to the 'next' URL or a default URL after successful login
        else:
            messages.error(request, "Username or password is incorrect")
            # If authentication fails, re-render the login page with an error message
            return render(request, 'signin.html', {'next': next_url})

    # For GET requests (including the initial visit to the login page), render the page normally
    # This ensures that an HttpResponse is returned even if the method is not POST
    return render(request, 'signin.html', {'next': next_url})


def signout(request):
    logout(request)
    # messages.success(request, "Logged Out Successfully")
    return redirect('signin')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect("home")
    else:
        return render(request, 'activation_failed.html')


@login_required  # Apply the login_required decorator to restrict access to authenticated users
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a property object without saving it to the database
            property = form.save(commit=False)
            # Set the user field to the currently logged-in user
            property.user = request.user
            property.save()  # Now save the property with the user set
            return redirect('property_list')  # Redirect to the property listing page
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form})


def property_list(request):
    properties = Property.objects.all()
    return render(request, 'property_list.html', {'properties': properties})


# views.py

def property_detail(request, id):
    # Retrieve the specific property by id
    property = get_object_or_404(Property, pk=id)

    # Determine if the current user is the owner of the property
    is_owner = request.user == property.user if request.user.is_authenticated else False

    # Include 'is_owner' in the context passed to the template
    context = {
        'property': property,
        'is_owner': is_owner,
    }

    return render(request, 'property_detail.html', context)


def profile_view(request):
    return render(request, 'profile.html')


def loan(request):
    return render(request, 'loan.html')


def guide(request):
    return render(request, 'guide.html')


def contact(request):
    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')


@login_required
def edit_property(request, id):
    property = get_object_or_404(Property, id=id)

    # Check if the user is the owner of the property
    if property.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this property.")

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property)
        formset = PropertyImageFormSet(request.POST, request.FILES, queryset=property.images.all())

        if form.is_valid() and formset.is_valid():
            form.save()
            instances = formset.save(commit=False)
            for instance in instances:
                instance.property = property  # Set the property_id for each image
                instance.save()
            formset.save_m2m()  # In case there are many-to-many relations to save
            return redirect('home')
    else:
        form = PropertyForm(instance=property)
        formset = PropertyImageFormSet(queryset=property.images.all())

    return render(request, 'edit_property.html', {'form': form, 'formset': formset})


@login_required
def delete_property(request, id):
    property = get_object_or_404(Property, id=id)

    # Check if the user is the owner of the property
    if property.user != request.user:
        return HttpResponseForbidden("You do not have permission to delete this property.")

    if request.method == "POST":
        property.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'property': property})


@login_required
def my_properties(request):
    user_properties = Property.objects.filter(user=request.user)
    return render(request, 'my_properties.html', {'properties': user_properties})


@login_required
def schedule_visit(request, property_id):
    property = get_object_or_404(Property, id=property_id)  # Get the property instance

    if request.method == 'POST':
        form = VisitScheduleForm(request.POST)
        if form.is_valid():
            visit_schedule = form.save(commit=False)
            visit_schedule.property = property  # Set the property
            visit_schedule.save()
            messages.success(request, 'Your visit has been scheduled successfully!')
            return redirect('user_schedule_requests')  # Adjust redirect as needed
    else:
        form = VisitScheduleForm()

    # Corrected render function call
    return render(request, 'schedule_visit.html', {'form': form, 'property_id': property_id})


@login_required
def accept_visit_schedule(request, schedule_id):
    visit_schedule = get_object_or_404(VisitSchedule, id=schedule_id, property__user=request.user)

    if visit_schedule.status == 'pending':
        visit_schedule.status = 'accepted'
        visit_schedule.save()
        messages.success(request, 'Visit schedule accepted successfully.')

        # Get the owner's email from the related Property instance
        property_owner_email = visit_schedule.property.email

        # Send an email notification from the property owner's email
        send_mail(
            'Visit Schedule Accepted',
            f'Hello {visit_schedule.name},\n\nYour visit schedule request for "{visit_schedule.property.title}" on {visit_schedule.preferred_date.strftime("%Y-%m-%d")} has been accepted.\n\n{visit_schedule.additional_notes}\n\nBest regards,',
            property_owner_email,  # Use property owner's email as the sender
            [visit_schedule.email],  # Recipient email address
            fail_silently=False,
        )

    else:
        messages.error(request, 'Invalid schedule status for acceptance.')

    return redirect('visit_schedule_list')


@login_required
def reject_visit_schedule(request, schedule_id):
    visit_schedule = get_object_or_404(VisitSchedule, id=schedule_id, property__user=request.user)

    if visit_schedule.status == 'pending':
        visit_schedule.status = 'rejected'
        visit_schedule.save()
        messages.success(request, 'Visit schedule rejected successfully.')

        # Assuming the property owner's email is to be used as the sender
        property_owner_email = visit_schedule.property.email

        # Send an email notification to the user who made the schedule
        send_mail(
            'Visit Schedule Rejected',
            f'Hello {visit_schedule.name},\n\nWe regret to inform you that your visit schedule request for "{visit_schedule.property.title}" on {visit_schedule.preferred_date.strftime("%Y-%m-%d")}" has been rejected.\n\n{visit_schedule.additional_notes}\n\nBest regards,',
            property_owner_email,  # Use the property owner's email or a generic sender email
            [visit_schedule.email],  # Recipient email address
            fail_silently=False,
        )

    else:
        messages.error(request, 'Invalid schedule status for rejection.')

    return redirect('visit_schedule_list')


@login_required
def visit_schedule_list(request):
    # Fetch properties owned by the user
    owned_properties = Property.objects.filter(user=request.user)

    # Fetch visit schedules for the user's properties made by others
    schedules_for_owned_properties = VisitSchedule.objects.filter(property__in=owned_properties).exclude(
        email=request.user.email)

    return render(request, 'visit_schedule_list.html', {'schedules': schedules_for_owned_properties})


@login_required
def user_schedule_requests(request):
    # Assuming each VisitSchedule has an 'email' field to identify the user
    user_schedules = VisitSchedule.objects.filter(email=request.user.email)
    return render(request, 'user_schedule_requests.html', {'schedules': user_schedules})


@login_required
def submit_offer(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    if request.method == "POST":
        offer_amount = request.POST.get('offer')
        user = request.user

        # Save the offer to the database
        offer = Offer(property=property, user=user, amount=offer_amount)
        offer.save()

        # Add a success message
        messages.success(request, 'Your offer has been submitted successfully!')

        return redirect(request.path)

    # If not a POST request or if there are other forms on the page, handle accordingly
    return render(request, 'property_detail.html', {'property': property})


def offer_list(request):
    # Assuming each offer has a foreign key to Property and Property has a foreign key to the User
    user_properties = Property.objects.filter(user=request.user)  # Get properties owned by the current user
    offers = Offer.objects.filter(property__in=user_properties)  # Get offers for those properties
    return render(request, 'offer_list.html', {'offers': offers})


stripe.api_key = settings.STRIPE_SECRET_KEY


def payment_form(request):
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'payment_form.html', context)


@require_POST
def process_payment(request):
    token = request.POST.get('stripeToken')

    try:
        # Charge the user's card
        charge = stripe.Charge.create(
            amount=1000,  # Amount in cents ($10.00)
            currency='usd',
            description='Example charge',
            source=token,
        )
        # If successful, redirect to a new URL for a success message
        return redirect('payment_success')
    except stripe.error.StripeError as e:
        # Handle error and redirect to a failure page or back to the payment form
        return redirect('payment_failure')


def payment_success(request):
    return render(request, 'payments/payment_success.html')


def payment_failure(request):
    return render(request, 'payments/payment_failure.html')


class AgentAuthBackend(BaseBackend):
    def authenticate(self, request, agent_id=None):
        try:
            agent = Agent.objects.get(agent_id=agent_id)
            print("Agent fetched:", agent)
            print("Associated User:", agent.user)
            return agent.user
        except Agent.DoesNotExist:
            print("No agent found with ID:", agent_id)
            return None

    def get_user(self, user_id):
        try:
            # `get_user` should return a User instance, not an Agent instance
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def agent_login(request):
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        password = request.POST.get('password')  # Get password from the form
        print("Agent ID received:", agent_id)  # Debugging

        # First, try to fetch the agent to get the associated user
        try:
            agent = Agent.objects.get(agent_id=agent_id)
            user = authenticate(request, username=agent.user.username, password=password)
        except Agent.DoesNotExist:
            user = None

        print("Authenticated user:", user)  # Debugging
        if user is not None:
            login(request, user)
            # Set the is_agent_session flag in the session
            request.session['is_agent_session'] = True
            return redirect('home')
        else:
            messages.error(request, 'Invalid Agent ID or Password')  # Display error message
    else:
        # If not a POST request, just render the login form
        messages.error(request, 'Invalid login method')

    return render(request, 'agent_login.html')


def agent_signup(request):
    if request.method == 'POST':
        form = AgentSignupForm(request.POST)
        if form.is_valid():
            # Save the associated User
            user = form.cleaned_data.get('user')
            if not user:
                # If no user is selected, create a new one
                username = form.cleaned_data.get('email')  # Use email as the username or generate one
                password = form.cleaned_data.get('password1')
                user = User.objects.create(
                    username=username,
                    email=form.cleaned_data.get('email'),
                    password=make_password(password)  # Make sure to hash the password
                )

            # Create or update the Agent
            agent, created = Agent.objects.update_or_create(
                user=user,
                defaults={
                    'name': form.cleaned_data.get('name'),
                    'agent_id': form.cleaned_data.get('agent_id'),
                    'email': form.cleaned_data.get('email'),
                    'phone_number': form.cleaned_data.get('phone_number'),
                    'is_approved': False  # Defaults to False until admin approval
                }
            )

            messages.success(request, "Your application has been submitted. Please wait for admin approval.")
            return redirect('agent_login')
        else:
            messages.error(request, form.errors)  # Display form errors
    else:
        form = AgentSignupForm()

    return render(request, 'agent_signup.html', {'form': form})


@login_required
def admin_dashboard(request):
    # Check if the logged-in user is the specific admin
    if request.user.email == settings.ADMIN_EMAIL:
        # Fetch pending agent applications
        pending_agents = Agent.objects.filter(is_approved=False)

        # Render the admin dashboard template with pending agents
        return render(request, 'admin_dashboard.html', {'pending_agents': pending_agents})
    else:
        # If the user's email does not match, show an error message or redirect
        messages.error(request, "You are not authorized to view the admin dashboard.")
        return redirect('home')


@require_POST
@staff_member_required
def approve_agent(request, agent_id):
    # The check if user is staff is redundant because of the @staff_member_required decorator
    agent = get_object_or_404(Agent, pk=agent_id)
    agent.is_approved = True
    agent.save()

    # Send approval email to agent directly in this function
    subject = 'Agent Account Approved'
    message = f'Hi {agent.name}, your agent account has been approved. You can now log in.'
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Use the email configured in settings.py
        [agent.email],  # Recipient email - the agent's email address
        fail_silently=False,
    )

    messages.success(request, "The agent has been approved successfully.")
    return redirect('admin_dashboard')


@require_POST
@staff_member_required
def reject_agent(request, agent_id):
    agent = get_object_or_404(Agent, pk=agent_id)
    # Update the agent's status to reflect rejection
    agent.is_approved = False
    agent.save()

    # Construct the rejection email to the agent
    subject = 'Agent Account Application Rejected'
    message = f'Hi {agent.name}, we regret to inform you that your agent account application has been rejected.'
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Sender email
        [agent.email],  # Recipient email - the agent's email address
        fail_silently=False,
    )

    messages.success(request, "The agent application has been rejected.")
    return redirect('admin_dashboard')


@login_required
def schedule_appointment(request):
    agents = Agent.objects.all()  # Fetch all agents

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            agent_id = request.POST.get('agent_id', None)
            if agent_id:
                try:
                    selected_agent = Agent.objects.get(id=agent_id)  # Fetch the selected Agent instance
                    # Use the User instance associated with the selected Agent for the 'agent' field
                    appointment = Appointment(
                        user=request.user,
                        agent=selected_agent.user,
                        date=form.cleaned_data['date'],
                        time=form.cleaned_data['time'],
                        notes=form.cleaned_data.get('notes', '')
                    )
                    appointment.save()
                    # Redirect or show a success message as needed
                    return redirect('appointment_success')  # Make sure you have a URL named 'appointment_success'
                except Agent.DoesNotExist:
                    # Handle the case where the selected agent does not exist
                    messages.error(request, 'Invalid Agent ID')
            else:
                messages.error(request, 'Agent ID is required')
        else:
            messages.error(request, 'There was a problem with the form. Please check your inputs.')
    else:
        form = AppointmentForm()

    # Pass the list of agents to the template for the dropdown
    return render(request, 'schedule_appointment.html', {'form': form, 'agents': agents})


@login_required
def appointment_success(request):
    return render(request, 'appointment_success.html')


@login_required
def agent_dashboard_view(request):
    try:
        # Assuming the Agent model has a user field that is a OneToOneField to the User model
        # This line attempts to get the Agent instance related to the logged-in User
        agent_user = request.user.agent.user
        # Filter appointments where the agent field matches the logged-in agent's User instance
        appointments = Appointment.objects.filter(agent=agent_user)
    except Agent.DoesNotExist:
        # If the logged-in User is not associated with an Agent, no appointments are returned
        appointments = []

    # Pass the appointments to the template
    return render(request, 'agent_dashboard.html', {'appointments': appointments})


def accept_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'accepted'
    appointment.save()
    send_mail(
        'Appointment Accepted',
        'Your appointment has been accepted.',
        'from@example.com',
        [appointment.user.email],
        fail_silently=False,
    )
    messages.success(request, "Appointment accepted and the user has been notified.")
    return redirect('agent_dashboard')


def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'rejected'
    appointment.save()
    send_mail(
        'Appointment Rejected',
        'Your appointment has been rejected.',
        'from@example.com',
        [appointment.user.email],
        fail_silently=False,
    )
    messages.success(request, "Appointment rejected and the user has been notified.")
    return redirect('agent_dashboard')
