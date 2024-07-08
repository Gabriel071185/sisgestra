from django.contrib.auth.forms import AuthenticationForm


########### Formulario ###########
class LoginForm(AuthenticationForm):
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs) 
        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].help_text = "Su numero de registro"
        self.fields["password"].widget.attrs["class"] = "form-control"
        self.fields["password"].help_text = "Su clave personal"