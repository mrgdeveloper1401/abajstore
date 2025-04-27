from django.urls import path,include
from django.contrib.auth.views import LogoutView
from .views import (UserRegisterView, UserLoginView, ForgetPasswordView, VerifyView, ResendOTPView, UserProfileView,
                    AddressListView, AddressDetailView, AddressCreateView, AddressUpdateView, AddressDeleteView)

app_name = "auth"

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name="register"),
    path('login/', UserLoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('forget-password/', ForgetPasswordView.as_view(), name='forget_password'),

    path('verify/', VerifyView.as_view(), name='verify'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),

    path('profile/', UserProfileView.as_view(), name='profile'),

    path('addresses/', AddressListView.as_view(), name='address_list'),
    path('address/<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
    path('address/new/', AddressCreateView.as_view(), name='address_create'),
    path('address/<int:pk>/edit/', AddressUpdateView.as_view(), name='address_update'),
    path('address/<int:pk>/delete/', AddressDeleteView.as_view(), name='address_delete'),
]
