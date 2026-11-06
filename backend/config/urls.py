from apps.accounts.views import CsrfView, LoginView, LogoutView, SessionView
from apps.core.views import LivenessView, ReadinessView
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

urlpatterns = [
    path("api/v1/", include("apps.catalog.urls")),
    path("api/v1/auth/csrf", CsrfView.as_view(), name="auth-csrf"),
    path("api/v1/auth/login", LoginView.as_view(), name="auth-login"),
    path("api/v1/auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("api/v1/auth/me", SessionView.as_view(), name="auth-me"),
    path("health/live", LivenessView.as_view(), name="health-live"),
    path("health/ready", ReadinessView.as_view(), name="health-ready"),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("django-admin/", admin.site.urls),
]
