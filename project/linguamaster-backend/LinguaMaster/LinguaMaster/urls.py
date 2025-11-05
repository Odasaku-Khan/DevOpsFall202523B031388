from django.contrib import admin
from django.urls import path
from authentification.views import RegisterView, LoginView

urlpatterns = [
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
]