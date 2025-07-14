# clinic/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Doctor, Patient
from .forms import DoctorRegistrationForm, PatientForm, CustomLoginForm


def user_login(request):
    """
    GET:  render login form
    POST: validate & authenticate, then redirect by role
    """
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember = request.POST.get('remember_me') == 'on'
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                if not remember:
                    request.session.set_expiry(0)  # expire on browser close

                # Role‐based redirect
                if user.role == 'doctor':
                    return redirect('doctor_dashboard')
                if user.role == 'receptionist':
                    return redirect('receptionist_dashboard')

                messages.error(request, 'Your account has no valid role.')
                logout(request)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    return render(request, 'clinic/login.html', {'form': form})


@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('login')

    total_patients = Patient.objects.count()
    recent_patients = Patient.objects.order_by('-created_at')[:5]

    return render(request, 'clinic/doctor_dashboard.html', {
        'total_patients': total_patients,
        'recent_patients': recent_patients,
    })


@login_required
def receptionist_dashboard(request):
    if request.user.role != 'receptionist':
        messages.error(request, 'Access denied.')
        return redirect('login')

    total_patients = Patient.objects.count()
    total_doctors  = Doctor.objects.count()
    recent_patients = Patient.objects.order_by('-created_at')[:5]

    return render(request, 'clinic/receptionist_dashboard.html', {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'recent_patients': recent_patients,
    })


@login_required
def add_doctor(request):
    if request.user.role != 'receptionist':
        messages.error(request, 'Only receptionists can add doctors.')
        return redirect('login')

    form = DoctorRegistrationForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Doctor added successfully!')
        return redirect('doctor_list')

    return render(request, 'clinic/add_doctor.html', {'form': form})


@login_required
def add_patient(request):
    if request.user.role not in ['doctor', 'receptionist']:
        messages.error(request, 'Access denied.')
        return redirect('login')

    form = PatientForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Patient added successfully!')
        return redirect('patient_list')

    return render(request, 'clinic/add_patient.html', {'form': form})


@login_required
def patient_list(request):
    if request.user.role not in ['doctor', 'receptionist']:
        messages.error(request, 'Access denied.')
        return redirect('login')

    q = request.GET.get('search', '')
    patients = Patient.objects.all()
    if q:
        patients = patients.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(patient_id__icontains=q) |
            Q(email__icontains=q)
        )
    paginator = Paginator(patients.order_by('-created_at'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'clinic/patient_list.html', {
        'page_obj': page_obj,
        'search_query': q,
    })


@login_required
def doctor_list(request):
    if request.user.role != 'receptionist':
        messages.error(request, 'Only receptionists can view doctors.')
        return redirect('login')

    q = request.GET.get('search', '')
    doctors = Doctor.objects.select_related('user')
    if q:
        doctors = doctors.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(specialization__icontains=q) |
            Q(license_number__icontains=q)
        )
    paginator = Paginator(doctors.order_by('-created_at'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'clinic/doctor_list.html', {
        'page_obj': page_obj,
        'search_query': q,
    })


@login_required
def patient_detail(request, patient_id):
    if request.user.role not in ['doctor', 'receptionist']:
        messages.error(request, 'Access denied.')
        return redirect('login')

    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'clinic/patient_detail.html', {'patient': patient})


@login_required
def edit_patient(request, patient_id):
    if request.user.role not in ['doctor', 'receptionist']:
        messages.error(request, 'Access denied.')
        return redirect('login')

    patient = get_object_or_404(Patient, id=patient_id)
    form = PatientForm(request.POST or None, request.FILES or None, instance=patient)
    if form.is_valid():
        form.save()
        messages.success(request, 'Patient updated successfully!')
        return redirect('patient_detail', patient_id=patient.id)

    return render(request, 'clinic/edit_patient.html', {
        'form': form,
        'patient': patient,
    })


def custom_logout(request):
    logout(request)
    return redirect('login')
