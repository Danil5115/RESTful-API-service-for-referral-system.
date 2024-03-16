from django.urls import path
from .views import CreateUserView, CreateReferralCodeView, DeleteActiveReferralCodeView, RetrieveReferralCodeByEmail, ReferralsListView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', CreateUserView.as_view(), name='register'),
    path('create-referral/', CreateReferralCodeView.as_view(), name='create_referral'),
    path('delete-referral-code/', DeleteActiveReferralCodeView.as_view(), name='delete_referral'),
    path('get-referral-code/', RetrieveReferralCodeByEmail.as_view(), name='get_referral_code_by_email'),
    path('user/<int:user_id>/referrals/', ReferralsListView.as_view(), name='user-referrals'),
    # Пути для JWT аутентификации
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]