from django.contrib import admin
from .models import Property, PropertyImage, VisitSchedule, Offer, Agent, Appointment


# Register your models here

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'price')  # Update with the fields you want to display in the admin list view.


# If you have additional settings for PropertyImage, you can create a similar admin class for it
admin.site.register(PropertyImage)
admin.site.register(VisitSchedule)
admin.site.register(Offer)
admin.site.register(Appointment)


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'agent_id', 'email', 'phone_number', 'is_approved', 'application_date')
