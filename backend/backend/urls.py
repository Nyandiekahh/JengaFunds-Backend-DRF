from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include('api.urls')),
    
    # API Documentation
    path('docs/', include_docs_urls(title='Jenga API Documentation')),
    
    # Redirect root to API documentation
    path('', RedirectView.as_view(url='/api/', permanent=False)),
]