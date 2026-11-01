from django.urls import include, path

from dashboard.views import (
    PositionCreateView,
    PositionDeleteView,
    PositionListView,
    PositionUpdateView,
    ShareCreateView,
    ShareDeleteView,
    ShareDetailView,
    ShareListView,
    ShareUpdateView,
)

app_name = "dashboard"

urlpatterns = [
    path("", ShareListView.as_view(), name="index"),
    path("<int:pk>", ShareDetailView.as_view(), name="detail"),
    path("create", ShareCreateView.as_view(), name="create"),
    path("update/<int:pk>", ShareUpdateView.as_view(), name="update"),
    path("delete/<int:pk>", ShareDeleteView.as_view(), name="delete"),
    path("portfolio/", PositionListView.as_view(), name="portfolio"),
    path(
        "portfolio/create",
        PositionCreateView.as_view(),
        name="portfolio_create",
    ),
    path(
        "portfolio/update/<int:pk>",
        PositionUpdateView.as_view(),
        name="portfolio_update",
    ),
    path(
        "portfolio/delete/<int:pk>",
        PositionDeleteView.as_view(),
        name="portfolio_delete",
    ),
    path("api/", include("dashboard.api.urls")),
]
