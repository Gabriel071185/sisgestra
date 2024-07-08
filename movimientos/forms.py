from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Movimiento, Transporte, Puesto, Operador, Ubicacion
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
import re


class CustomUser(UserCreationForm):
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
        help_text="Debe contener una mayúscula, una minúscula y un caracter alfanumérico",
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control" }),
        strip=False,
        help_text="Ingrese la misma contraseña que antes",
    )

    class Meta:
        model = User
        fields = ["username", 'email', "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "username": "Obligatorio. Utilizar su numero de registro",
        }
        
    def clean_username(self):

        user = self.cleaned_data["username"]
        regex = r'^\d{5}$'
        if re.match(regex, user) is None:
            raise ValidationError('Código Invalido')
        return user
    

class MovimientoForm(ModelForm):
    cargado = forms.ChoiceField(label="Estado de carga", widget=forms.RadioSelect({'class': 'form-radio-input'}),choices=[(1, "Cargado"), (0, "Descargado")], required=True)
    class Meta:
        
        model = Movimiento
        widgets = {'transporte': forms.Select(attrs={'class': 'form-select'}),
                   'descripcion_carga': forms.Textarea(attrs={'class': 'form-control'}),
                   'ubicacion_final': forms.Select(attrs={'class': 'form-select'}),}
        
        fields = ['transporte', 'descripcion_carga','ubicacion_final', 'cargado']

    def clean(self):
        data = super().clean()
        cargado = int(data['cargado'])
        ubicacion_final = data['ubicacion_final']
        transporte = data['transporte']
        print((ubicacion_final.codigo_porton != "En espera" and transporte.ultima_ubicacion.codigo_porton != "En espera"))
        if transporte.cargado == bool(cargado) and (ubicacion_final.codigo_porton != "En espera" and transporte.ultima_ubicacion.codigo_porton != "En espera"):
            self.add_error('cargado', f'El transporte ya se encuentra {"cargado" if cargado else "descargado"}')
        if bool(cargado) and ubicacion_final.codigo_porton == "Playa" :
            self.add_error('ubicacion_final', 'No puede haber un semi cargado en playa')


    def clean_ubicacion_final(self):
        ubicacion = self.cleaned_data['ubicacion_final']
        if ubicacion is not None:
            if Transporte.objects.filter(ultima_ubicacion = ubicacion).exclude(ultima_ubicacion__codigo_porton = "Playa").exists():
                raise ValidationError(f'Ubicación ocupada.')
        return ubicacion

    
class OperadorForm(ModelForm):
    class Meta:
        model = Operador
        fields = '__all__'
        

       
        
class PuestoForm(ModelForm):
    datos_operador = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del operador'}), required=False, help_text='Número de registro - Apellido')
    class Meta:
        model = Puesto
        fields = ['nombre_puesto','operador','datos_operador', 'rol']

    def clean_nombre_puesto(self):
        return self.cleaned_data['nombre_puesto'].capitalize()

    def clean(self):
        data = super().clean()
        
        operador = data.get('operador')
        datos_operador = data.get('datos_operador')

        # Si lleno ambos - Mal
        if operador and datos_operador:
            raise ValidationError('Que no entendiste de que es uno o el otro')
        # Si cargo uno nuevo
        if datos_operador:
            # Si no tiene el formato deseado
            if '-' not in datos_operador:
                self.add_error('datos_operador', 'Respete el formato solicitado')
                return
            registro = datos_operador.split('-')[0].strip()
            # Comprobamos el numero de registro
            if re.match(r'^\d{5}$', registro) is None:
                raise ValidationError('Registro Invalido')
                return
            nombre = datos_operador.split('-')[1].title()
            datos_operador = ' - '.join([registro, nombre])
            # Creamos o devolvemos si ya existe
            operador, created = Operador.objects.get_or_create(datos_operador = datos_operador)

        # Si ya está asignado a un puesto
        
        if Puesto.objects.filter(operador = operador).exists():
            raise ValidationError('El operador ya tiene un puesto asignado en este momento')

        # Le dejamos la referencia al objeto
        self.cleaned_data['operador'] = operador

        

