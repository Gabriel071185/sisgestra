from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import CustomUser, MovimientoForm, PuestoForm
from django.contrib.auth import authenticate, login
from .models import Movimiento, Transporte, Ubicacion, Puesto, Operador
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Case, Value, When
from datetime import datetime
from email.mime.image import MIMEImage
from django.core.exceptions import ValidationError


# Create your views here.

def index(request):
    return redirect(reverse('login'))


    

def registro(request):
    if request.user.is_authenticated: return redirect(reverse("movimientos:panel_inicio"))
    data = {'form': CustomUser(), 'activo': 'registro'}
    if request.method == 'POST':
        data['form'] = CustomUser(request.POST)
        if data['form'].is_valid():
            data['form'].save()
            user = authenticate(username=data['form'].cleaned_data['username'], password=data['form'].cleaned_data['password1'])
            login(request, user)
            messages.success(request, 'Te has registrado exitosamente')
            asunto = "Registro exitoso en sigestra"
            mensaje = render_to_string('email_generator.html', {'user': request.user , 'fecha': datetime.now()})
            email = EmailMessage(asunto, mensaje, to=[user.email])
            email.content_subtype = 'html'
            
            email.send()
            return redirect(reverse("movimientos:panel_inicio"))

    return render(request, 'registration/registro.html', data)
   

def panel_inicio(request):
    movimientos = Movimiento.objects.all().order_by('-tiempo')[:10]
    if 'filtro' in request.GET and request.GET.get('filtro') == 'ubicacion':
        movimientos = Movimiento.objects.alias(priority=Case(
            When(ubicacion_final__codigo_porton = "Playa", then = Value(0)),
            default=Value(1)
        )).order_by('priority', '-ubicacion_final')
    if request.method == "POST":
        asunto = "Reporte de sigestra"
        mensaje = render_to_string('reporte.html', {'movimientos': movimientos, 'fecha': datetime.now(), 'user': request.user, 'puestos': Puesto.objects.all()})
        email = EmailMessage(asunto, mensaje, to=[request.user.email])
        email.content_subtype = 'html'
        email.send()
        messages.success(request, 'El correo se ha enviado exitosamente')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect(reverse("movimientos:panel_inicio"))


    return render(request, 'panel_inicio.html', {'movimientos': movimientos, 'activo': 'inicio',})
   
@login_required   
def panel_movimientos(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            if movimiento.ubicacion_final is None:
                ubicacion, created = Ubicacion.objects.get_or_create(codigo_porton = "Playa")
                movimiento.ubicacion_final = ubicacion
            movimiento.save()
            transporte = Transporte.objects.get(pk = movimiento.transporte.pk)

            transporte.cargado = bool(int(form.cleaned_data['cargado']))

            transporte.save()
            messages.success(request, 'Tu movimiento se realizo exitosamente')
            return redirect(reverse('movimientos:panel_inicio',)) 
        else:
            messages.error(request, 'Hay errores en el formulario') 
    else:
        form = MovimientoForm()
    return render(request, 'panel_movimientos.html', {'form': form, 'activo': 'carga_movimientos'} )



@login_required
def panel_reportes(request, id):
    movimiento = Movimiento.objects.get(pk=id)
    return render(request, 'panel_reportes.html',{'movimiento': movimiento, 'activo': 'panel_reporte'})

@login_required
def editar_movimiento(request, id):
    movimiento = Movimiento.objects.get(pk=id)
    if request.user != movimiento.usuario and request.user.is_superuser == False:
        messages.error(request, 'Solo el usuario registrado puede editar este movimiento')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect(reverse("movimientos:panel_inicio"))
    if request.method == 'POST':
        form = MovimientoForm(request.POST, instance=movimiento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu movimiento se editó exitosamente')
            return redirect(reverse('movimientos:panel_inicio',))
    else:
        form = MovimientoForm(instance=movimiento)
    
    return render(request, 'panel_movimientos.html', {'form': form})

@login_required
def eliminar_movimiento(request, id):
    movimiento = Movimiento.objects.get(pk=id)
    if request.user != movimiento.usuario and request.user.is_superuser == False:
        messages.error(request, 'Solo el usuario que registró este movimiento puede eliminar el mismo')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect(reverse("movimientos:panel_inicio"))
    movimiento.delete()
    messages.success(request, 'Tu movimiento se eliminó exitosamente')
    return redirect(reverse('movimientos:panel_inicio',))

@login_required
def descargar_movimiento(request, id):
    movimiento = Movimiento.objects.get(pk=id)
    if request.user != movimiento.usuario and request.user.is_superuser == False:
        messages.error(request, 'Solo el usuario que registró este movimiento puede descargar el mismo')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect(reverse("movimientos:panel_inicio"))
    playa = Ubicacion.objects.get(codigo_porton = "Playa")
    movimiento.ubicacion_final = playa
    movimiento.descripcion_carga = "Vacío"
    movimiento.transporte.ultima_ubicacion = playa
    movimiento.transporte.cargado = False
    movimiento.transporte.save()
    movimiento.save()
    messages.success(request, 'Tu descarga se realizó exitosamente y el transporte ya no se encuentra cargado')
    return redirect(reverse('movimientos:panel_inicio',))


# Vistas de los Reportes

@login_required
def parte_operadores(request):
    form = PuestoForm(request.POST)
    if request.method == "POST":
        
        if form.is_valid():
            instancia = form.save(commit=False)
            instancia.usuario = request.user
            instancia.save()
            messages.success(request, 'El operador/puesto se ha registrado exitosamente')
            return redirect(reverse('movimientos:panel_reporte_operadores'))
    return render(request, 'panel_operadores.html', {'form': form, 'activo': 'carga_personal'})


@login_required
def panel_reportes_operadores(request):
    puestos = Puesto.objects.all()
    return render(request, 'panel_reporte_operadores.html' , {'puestos': puestos, 'activo': 'reporte_personal'})


def puesto_operadores_eliminar(request, id):
    puestos = Puesto.objects.get(pk=id)
    if request.user != puestos.usuario and request.user.is_superuser == False:
        messages.error(request, 'Solo el usuario registrado puede eliminar este operador')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect(reverse("movimientos:panel_reporte_operadores"))
        
    puestos.delete()
    messages.success(request, 'El operador se ha eliminado exitosamente')
    return redirect(reverse('movimientos:panel_reporte_operadores'))      

@login_required
def puesto_operadores_editar(request, id):
    puestos = Puesto.objects.get(pk=id)
    if request.user != puestos.usuario and request.user.is_superuser == False:
        messages.error(request, 'Solo el usuario registrado puede editar este operador')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect(reverse("movimientos:panel_reporte_operadores"))
    if request.method == 'POST':
        form = PuestoForm(request.POST, instance=puestos)
        if form.is_valid():
            form.save()
            messages.success(request, 'El operador se ha editado exitosamente')
            return redirect(reverse('movimientos:panel_reporte_operadores'))
    else:
        form = PuestoForm(instance=puestos)
    
    return render(request, 'panel_operadores.html', {'form': form})