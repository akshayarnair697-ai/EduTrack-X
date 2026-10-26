from django.urls import path
from . import views

app_name = 'Guest'

urlpatterns = [
    path('', views.index, name='index'),
    path('Login/', views.Login, name='Login'),
    path('StudentRegister/', views.StudentRegister, name='StudentRegister'),
    path('CompanyRegister/', views.CompanyRegister, name='CompanyRegister'),
    path('Logout/', views.Logout, name='Logout'),
]
