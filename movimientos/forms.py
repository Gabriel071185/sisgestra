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
        ubicacion_final = data.get('ubicacion_final')
        transporte = data['transporte']
        if ubicacion_final is None:
            return
        
        if bool(cargado) and ubicacion_final.codigo_porton == "Playa" :
            self.add_error('ubicacion_final', 'No puede haber un semi cargado en playa')


    def clean_ubicacion_final(self):
        ubicacion = self.cleaned_data['ubicacion_final']
        if ubicacion is not None:
            if Transporte.objects.filter(ultima_ubicacion__codigo_porton = ubicacion).exclude(ultima_ubicacion__codigo_porton = "Playa").exists():
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

        
        if operador and datos_operador:
            raise ValidationError('No puedes completar los dos campos, debes elegir uno')
       
        if datos_operador:
            
            if '-' not in datos_operador:
                self.add_error('datos_operador', 'Respete el formato solicitado')
                return
            registro = datos_operador.split('-')[0].strip()
            
            if re.match(r'^\d{5}$', registro) is None:
                raise ValidationError('Registro Invalido')
                return
            nombre = datos_operador.split('-')[1].title()
            datos_operador = ' - '.join([registro, nombre])
            
            operador, created = Operador.objects.get_or_create(datos_operador = datos_operador)

        
        
        if Puesto.objects.filter(operador = operador).exists():
            raise ValidationError('El operador ya tiene un puesto asignado en este momento')

        
        self.cleaned_data['operador'] = operador

        

