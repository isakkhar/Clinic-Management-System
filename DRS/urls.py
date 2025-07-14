# clinic/urls.py

from django.urls import path
from .views import (
    user_login, custom_logout,
    doctor_dashboard, receptionist_dashboard,
    add_doctor, add_patient,
    patient_list, doctor_list,
    patient_detail, edit_patient,
)

urlpatterns = [
    # serve login form at `/`
    path('', user_login, name='login'),
    path('logout/',             custom_logout,            name='logout'),

    # dashboards
    path('doctor/dashboard/',   doctor_dashboard,         name='doctor_dashboard'),
    path('receptionist/dashboard/', receptionist_dashboard, name='receptionist_dashboard'),

    # doctor & patient CRUD
    path('doctor/add/',        add_doctor,               name='add_doctor'),
    path('patients/add/',      add_patient,              name='add_patient'),
    path('patients/',          patient_list,             name='patient_list'),
    # path('patients/delete/', delete_patient, name='delete_patient'),
    path('doctors/',           doctor_list,              name='doctor_list'),
    path('patients/<int:patient_id>/',      patient_detail, name='patient_detail'),
    path('patients/<int:patient_id>/edit/', edit_patient,   name='edit_patient'),
]
