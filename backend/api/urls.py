# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.dashboard_views import DashboardViewSet
from .views.loan_views import LoanViewSet, LoanTypeViewSet
from .views.transaction_views import TransactionViewSet
from .views.investment_views import InvestmentViewSet
from .views.document_views import LoanDocumentViewSet
from .views.auth_views import (
    login, register, verify_email,
    request_password_reset, reset_password,
    change_password, logout, get_user_profile
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'loan-types', LoanTypeViewSet)
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'investments', InvestmentViewSet, basename='investment')

# Define nested routes for documents
loans_router = DefaultRouter()
loans_router.register(r'documents', LoanDocumentViewSet, basename='loan-document')

urlpatterns = router.urls + [
    # Existing auth endpoints
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/verify-email/', verify_email, name='verify-email'),
    path('auth/password-reset/', request_password_reset, name='password-reset-request'),
    path('auth/password-reset/confirm/', reset_password, name='password-reset-confirm'),
    path('auth/change-password/', change_password, name='change-password'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', get_user_profile, name='user-profile'),
    
    # Nested document routes
    path('loans/<int:loan_pk>/', include(loans_router.urls)),
]