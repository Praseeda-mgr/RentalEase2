from django.contrib import admin

# Register your models here.
from .models import *
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'location', 'approval_status', 'is_available')
    list_filter = ('approval_status', 'is_available', 'location')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Booking)

