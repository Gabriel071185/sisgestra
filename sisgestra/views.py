from django.contrib.auth.views import LoginView
from .forms import LoginForm
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages

class Login(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated: 
            return redirect(reverse("movimientos:panel_inicio"))
        
            
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activo'] = 'iniciar_sesion'
        return context    
    def form_invalid(self, form):
        messages.error(self.request, 'Credenciales inválidas')
        return super().form_invalid(form)
        
    

