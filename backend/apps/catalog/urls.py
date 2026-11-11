from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.accounts.management_api import UserViewSet
from apps.core.editorial_api import AdminSettingsView, AuditViewSet, PublicSettingsView
from apps.documents.views import (
    CoverView,
    DocumentFileView,
    JobView,
    PublicFileView,
    RetryView,
    UploadView,
)

from .people_api import PersonViewSet
from .views import (
    AdminPublicationViewSet,
    CatalogSummaryView,
    CategoryViewSet,
    PublicCategoryViewSet,
    PublicPublicationViewSet,
    RatingView,
)

router = SimpleRouter(trailing_slash=False)
router.register("public/publications", PublicPublicationViewSet, basename="public-publications")
router.register("public/categories", PublicCategoryViewSet, basename="public-categories")
router.register("admin/publications", AdminPublicationViewSet, basename="admin-publications")
router.register("admin/categories", CategoryViewSet, basename="admin-categories")
router.register("admin/users", UserViewSet, basename="admin-users")
router.register("admin/people", PersonViewSet, basename="admin-people")
router.register("admin/audit", AuditViewSet, basename="admin-audit")
urlpatterns = [
    path("public/catalog", CatalogSummaryView.as_view()),
    path("public/settings", PublicSettingsView.as_view()),
    path("admin/settings", AdminSettingsView.as_view()),
    path("admin/uploads", UploadView.as_view()),
    path("admin/jobs/<uuid:pk>", JobView.as_view()),
    path("admin/jobs/<uuid:pk>/retry", RetryView.as_view()),
    path("admin/jobs/<uuid:pk>/cover", CoverView.as_view()),
    path("admin/files/<uuid:pk>", DocumentFileView.as_view()),
    path("public/publications/<slug:slug>/rating", RatingView.as_view()),
    path("public/publications/<slug:slug>/<str:kind>", PublicFileView.as_view()),
    *router.urls,
]
