from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('receptionist', 'Receptionist'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,11}$',
        message="Phone number must be entered in the format: '+880123456789'. Up to 11 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=11, blank=True)
    address = models.TextField(blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    # license_number = models.CharField(max_length=50, unique=True)
    # experience_years = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # available_days = models.CharField(max_length=200, help_text="e.g., Mon, Tue, Wed")
    # available_time = models.CharField(max_length=100, help_text="e.g., 9:00 AM - 5:00 PM")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    patient_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,11}$',
        message="Phone number must be entered in the format: '+880123456789'. Up to 11 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=11)
    address = models.TextField()
    # date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    emergency_contact = models.CharField(max_length=17, blank=True)
    image = models.ImageField(upload_to='patient_images/', blank=True, null=True)
    # medical_history = models.TextField(blank=True)
    # allergies = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.patient_id}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.patient_id:
            # Generate patient ID
            import datetime
            today = datetime.date.today()
            prefix = f"P{today.year}{today.month:02d}"
            last_patient = Patient.objects.filter(
                patient_id__startswith=prefix
            ).order_by('patient_id').last()

            if last_patient:
                last_number = int(last_patient.patient_id[-4:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.patient_id = f"{prefix}{new_number:04d}"

        super().save(*args, **kwargs)
