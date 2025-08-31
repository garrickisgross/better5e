from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import SignupForm
from django.contrib.auth.mixins import LoginRequiredMixin

class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        # Auto-login after successful signup
        login(self.request, self.object)
        return response

    def get_success_url(self):
        return reverse_lazy("core:home")


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/settings.html"
