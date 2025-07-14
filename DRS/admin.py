from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Doctor, Patient

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address', 'image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address', 'image')}),
    )

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'consultation_fee')
    list_filter = ('specialization',)
    search_fields = ('user__first_name', 'user__last_name', 'specialization')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'first_name', 'last_name', 'email', 'phone_number', 'created_at')
    list_filter = ('gender', 'blood_group', 'created_at')
    search_fields = ('patient_id', 'first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('patient_id', 'created_at', 'updated_at')

admin.site.register(User, CustomUserAdmin)
