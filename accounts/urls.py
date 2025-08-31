from django.urls import path
from .views import SignupView, AccountSettingsView

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("settings/", AccountSettingsView.as_view(), name="settings"),
]
