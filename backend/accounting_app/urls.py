from django.urls import path
from . import views

urlpatterns = [
    path(
        "auth/register/",
        views.LoginSystem.as_view({"post": "register_view"}),
        name="register",
    ),
    path("auth/login/", views.LoginSystem.as_view({"post": "login_view"}), name="login"),
    path("auth/logout/", views.LoginSystem.as_view({"post": "logout_view"}), name="logout"),
    path("users/", views.LoginSystem.as_view({"get": "user_view"}), name="user-list"),
    path("api/auth/password-reset/", views.PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset/<uidb64>/<token>/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "transactions/",
        views.TransactionListCreateView.as_view(),
        name="transactions-list-create",
    ),
    path(
        "transactions/<int:id>/",
        views.TransactionGetDeleteUpdateView.as_view(),
        name="transactions_get_delete_update",
    ),
    path(
        "categories/",
        views.CategoryListCreateView.as_view(),
        name="categories-list-create",
    ),
    path(
        "categories/<int:id>/",
        views.CategoryGetDeleteUpdateView.as_view(),
        name="categories_get_delete_update",
    ),
]
