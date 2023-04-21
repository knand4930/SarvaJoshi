from django.urls import path, re_path, include
from main.views import *
from rest_framework import routers
from knox.views import LogoutView

router = routers.DefaultRouter()
router.register(r'user-register', RegisterView, basename='task')
router.register(r'api/user/profile', UserProfile, basename='user_profile')

urlpatterns = [
    path('', include(router.urls)),
    path('get-login-otp-mobile/', ValidatePhoneSendOTP.as_view(), name='get-login-otp-mobile'),
    path('verify-login-otp-mobile/', VerifyPhoneOTPView.as_view(), name='login-otp-verify'),
    path('logout/', LogoutView.as_view(), name='knox_logout'),
    # path('api/register/', RegisterView.as_view(), name='register_view'),
    # path('api/register/otp/', otp, name="otp_register"),
    # path('api/login/attempt/', LoginAttemptView.as_view(), name='login_attempt'),
    # path('api/login/otp/', LoginOtpView.as_view(), name='login_otp'),
    path('api/user/update/<int:user_id>', UserRetrieveUpdateAPIView.as_view(), name='user_update'),
    # path('api/user/profile/', UserProfile.as_view(), name="user_profile"),
    path('api/update/profile/<int:pk>/', UpdateProfileView.as_view(), name='auth_update_profile'),
]