from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User, Doctor, Patient
from .forms import DoctorRegistrationForm, PatientForm, CustomLoginForm


def home(request):
    return render(request, 'clinic/home.html')


def user_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                # Role-based redirection
                if user.role == 'doctor':
                    return redirect('doctor_dashboard')
                elif user.role == 'receptionist':
                    return redirect('receptionist_dashboard')
                else:
                    messages.error(request, 'Invalid user role')
                    return redirect('login')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = CustomLoginForm()

    return render(request, 'clinic/login.html', {'form': form})


@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('login')

    total_patients = Patient.objects.count()
    recent_patients = Patient.objects.order_by('-created_at')[:5]

    context = {
        'total_patients': total_patients,
        'recent_patients': recent_patients,
    }
    return render(request, 'clinic/doctor_dashboard.html', context)


@login_required
def receptionist_dashboard(request):
    if request.user.role != 'receptionist':
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('login')

    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    recent_patients = Patient.objects.order_by('-created_at')[:5]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'recent_patients': recent_patients,
    }
    return render(request, 'clinic/receptionist_dashboard.html', context)


@login_required
def add_doctor(request):
    if request.user.role != 'receptionist':
        messages.error(request, 'Access denied. Only receptionists can add doctors.')
        return redirect('login')

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor added successfully!')
            return redirect('doctor_list')
    else:
        form = DoctorRegistrationForm()

    return render(request, 'clinic/add_doctor.html', {'form': form})


@login_required
def add_patient(request):
    if request.user.role not in ['doctor', 'receptionist']:
        messages.error(request, 'Access denied. You are not authorized to perform this action.')
        return redirect('login')

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient added successfully!')
            return redirect('patient_list')
    else:
        form = PatientForm()

    return render(request, 'clinic/add_patient.html', {'form': form})


@login_required
def patient_list(request):
    if request.user.role not in ['doctor', 'receptionist']:
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('login')

    search_query = request.GET.get('search', '')
    patients = Patient.objects.all()

    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(patient_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    patients = patients.order_by('-created_at')
    paginator = Paginator(patients, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'clinic/patient_list.html', context)


@login_required
def doctor_list(request):
    if request.user.role != 'receptionist':
        messages.error(request, 'Access denied. Only receptionists can view doctor list.')
        return redirect('login')

    search_query = request.GET.get('search', '')
    doctors = Doctor.objects.select_related('user').all()

    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(license_number__icontains=search_query)
        )

    doctors = doctors.order_by('-created_at')
    paginator = Paginator(doctors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'clinic/doctor_list.html', context)


@login_required
def patient_detail(request, patient_id):
    if request.user.role not in ['doctor', 'receptionist']:
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('login')

    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'clinic/patient_detail.html', {'patient': patient})


@login_required
def edit_patient(request, patient_id):
    if request.user.role not in ['doctor', 'receptionist']:
        messages.error(request, 'Access denied. You are not authorized to perform this action.')
        return redirect('login')

    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient updated successfully!')
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = PatientForm(instance=patient)

    return render(request, 'clinic/edit_patient.html', {'form': form, 'patient': patient})


def custom_logout(request):
    logout(request)
    return redirect('login')