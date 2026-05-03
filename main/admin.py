from django.contrib import admin
from .models import Pet, AdoptionRequest, ContactMessage, Notification
from django.utils.html import format_html

# admin.py
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'breed', 'age', 'category', 'gender', 'available', 'created_at')
    
    # If the migration worked, 'created_at' should be here:
    fields = ('name', 'breed', 'age', 'description', 'category', 'gender', 'image', 'available', 'is_special_needs', 'created_at')

@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    # 1. Added rejection_reason to the list view
    list_display = ('user', 'pet', 'status', 'rejection_reason', 'created_at')
    list_filter = ('status', 'created_at', 'pet')
    search_fields = ('full_name', 'email', 'phone', 'pet__name')

    readonly_fields = ('created_at',)

    fieldsets = (
        ('Adopter Info', {
            'fields': ('user', 'full_name', 'email', 'phone', 'age', 'address', 'city', 'occupation')
        }),
        ('Housing Info', {
            'fields': ('housing_type', 'own_or_rent', 'landlord_permission')
        }),
        ('Pet Experience', {
            'fields': ('previous_pet', 'current_pet', 'experience', 'reason')
        }),
        ('Documents', {
            # Note: added selfie_with_pet since it's in your models.py
            'fields': ('photo_id', 'legal_doc', 'selfie_with_pet')
        }),
        ('Admin Status', {
            # 2. Added rejection_reason here so you can type it in the detail view
            'fields': ('status', 'rejection_reason', 'created_at')
        }),
    )

    def photo_id_link(self, obj):
        if obj.photo_id:
            return format_html('<a href="{}" target="_blank">View Photo ID</a>', obj.photo_id.url)
        return "-"
    photo_id_link.short_description = "Photo ID"

    def legal_doc_link(self, obj):
        if obj.legal_doc:
            return format_html('<a href="{}" target="_blank">View Legal Doc</a>', obj.legal_doc.url)
        return "-"
    legal_doc_link.short_description = "Legal Document"

    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        # When approving, we clear the rejection reason
        queryset.update(status='Approved', rejection_reason="")
    approve_requests.short_description = "Mark selected requests as Approved"

    def reject_requests(self, request, queryset):
        # Default reason for bulk rejection
        queryset.update(status='Rejected', rejection_reason="Criteria not met.")
    reject_requests.short_description = "Mark selected requests as Rejected"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'created_at', 'replied')
    list_filter = ('replied', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('user', 'name', 'email', 'message', 'created_at')    

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'user__username')