from django.shortcuts import render
from django.views.generic import CreateView, FormView
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.urls import reverse_lazy

from .forms import LoginForm, RegisterForm, GuestForm
from .models import GuestEmail

# Create your views here.


class RegisterView(CreateView):
  form_class = RegisterForm
  template_name = 'accounts/register.html'
  success_url = reverse_lazy('accounts:login')

class LoginView(FormView):
  form_class = LoginForm
  template_name = 'accounts/login.html'
  success_url = reverse_lazy('home')

  def form_valid(self, form):
    request = self.request
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    email = form.cleaned_data.get("email")
    password = form.cleaned_data.get("password")
    user = authenticate(request, username=email, password=password)
    if user is not None:
      login(request, user)
      try:
        del request.session['guest_email_id']
      except:
        pass
      if is_safe_url(redirect_path, request.get_host()):
        return redirect(redirect_path)
      else:
        return redirect("home")
    return super(LoginView, self).form_invalid(form)


def guest_register_view(request):
  form = GuestForm(request.POST or None)
  context = {
    "form": form
  }
  next_ = request.GET.get('next')
  next_post = request.POST.get('next')
  redirect_path = next_ or next_post or None
  if form.is_valid():
    email = form.cleaned_data.get("email")
    new_guest_email = GuestEmail.objects.create(email=email)
    request.session['guest_email_id'] = new_guest_email.id
    if is_safe_url(redirect_path, request.get_host()):
      return redirect(redirect_path)
    else:
      return redirect("accounts:register")
  return redirect("accounts:register")