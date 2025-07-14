from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Doctor, Patient


class DoctorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=17, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    image = forms.ImageField(required=False)

    # Doctor specific fields
    # specialization = forms.CharField(max_length=100, required=True)
    # license_number = forms.CharField(max_length=50, required=True)
    # experience_years = forms.IntegerField(min_value=0, required=True)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    # available_days = forms.CharField(max_length=200, required=True)
    # available_time = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number',
                  'address', 'image', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        user.image = self.cleaned_data.get('image')

        if commit:
            user.save()

            # Create doctor profile
            Doctor.objects.create(
                user=user,
                # specialization=self.cleaned_data['specialization'],
                # license_number=self.cleaned_data['license_number'],
                # experience_years=self.cleaned_data['experience_years'],
                consultation_fee=self.cleaned_data['consultation_fee'],
                # available_days=self.cleaned_data['available_days'],
                # available_time=self.cleaned_data['available_time']
            )

        return user


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address',
                   'gender', 'blood_group', 'emergency_contact',
                  'image']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            # 'medical_history': forms.Textarea(attrs={'rows': 4}),
            # 'allergies': forms.Textarea(attrs={'rows': 3}),
        }


class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)