from django.contrib.auth.views import LoginView
from .forms import LoginForm

class Login(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm


